from inspect import getmro

try:
    from zope.interface import classImplements
    from zope.interface import implementedBy
    ZOPE_INTERFACE_AVAILABLE = True
except ImportError:                   #pragma NO COVERAGE
    ZOPE_INTERFACE_AVAILABLE = False  #pragma NO COVERAGE


from metachao._instructions import Instruction
from metachao._instructions import overwrite
from metachao._instructions import plumb
from metachao.prototype import prototype_property
from metachao import utils

from ._compose import compose
from ._instructions import child as child_instruction
from ._instructions import config as config_instruction
from .utils import getmembers


DICT_KEYS_OF_PLAIN_CLASS = ['__dict__', '__doc__', '__module__', '__weakref__']


class ConfigError(Exception):
    pass


class UnknownConfigKeys(ConfigError, KeyError):
    pass


class Workbench(object):
    def __init__(self, origin):
        self.origin = origin
        self.dct = dict(
            __metachao_aspects__=getattr(origin, '__metachao_aspects__', [])[:]
        )
        if utils.isclass(origin):
            # Aspect application does not change the name. This can
            # lead to messages like "... expects a.A not a.A".
            self.name = origin.__name__
            self.baseclasses = (origin,)
            self.type = type(origin)

            # Aspect application does not change the module. If that
            # is not what you want, consider subclassing first.
            # XXX: it totally should indicate that sth is different
            #self.dct['__module__'] = origin.__module__
            self.dct['__doc__'] = origin.__doc__
        else:
            # we are pretty much creating an object that uses origin
            # as prototype.
            self.name = "Prototyper:%s" % (origin.__class__.__name__,)
            self.baseclasses = ()
            self.type = type

            # bound methods found on origin, except if blacklisted
            blacklist = (
                '__class__', '__delattr__', '__doc__', '__format__',
                '__getattribute__', '__hash__',
                '__init__', '__metachao_origin__',
                '__metachao_prototype__', '__new__', '__reduce__',
                '__reduce_ex__', '__repr__', '__setattr__',
                '__sizeof__', '__str__', '__subclasshook__',
            )
            self.dct.update(((k, getattr(origin, k))
                             for k, v in getmembers(origin)
                             if callable(v) and not k in blacklist))

            # properties bound to origin for all properties found on
            # origin's class
            self.dct.update(((k, prototype_property(origin, v))
                             for k, v in getmembers(origin.__class__)
                             if type(v) is property))

            # getattr fallback to origin, setattr and delattr on new
            self.dct['__getattr__'] = lambda _, name: getattr(origin, name)

            # empty __init__ needed if a later aspect plumbs it
            self.dct['__init__'] = lambda *a, **kw: None
            self.dct['__metachao_prototype__'] = origin

            self.dct['__doc__'] = origin.__doc__

        if '__metachao_effective__' in getattr(origin, '__dict__', ()):
            self.dct['__metachao_effective__'] = \
                origin.__metachao_effective__.copy()


class _UNSET(object):
    pass


def parse_aspect(aspect):
    config = dict()
    instructions = dict()
    seen = list()
    children = dict()

    # walk the mro, w/o object, gathering/creating instructions
    # XXX: not sure whether that is good
    # XXX: why doesn't getmembers do the job?
    for cls in getmro(aspect)[:-1]:
        for name, item in cls.__dict__.iteritems():
            # ignored attributes
            if name.startswith('_abc_'):
                continue
            if name == '__abstractmethods__':
                continue
            if name.startswith('__metachao_'):
                continue
            if name in (
                    '__implemented__', '__metaclass__',
                    '__provides__', '__providedBy__',
            ):
                continue
            if name in DICT_KEYS_OF_PLAIN_CLASS:
                continue

            if name in seen:
                continue
            seen.append(name)

            if isinstance(item, child_instruction):
                key = getattr(item, 'key', name)
                children[key] = item
                continue

            # undecorated items are understood as overwrite
            if isinstance(item, Instruction):
                instruction = item
            else:
                instruction = overwrite(item)

            instruction.name = name
            instruction.parent = cls
            instructions[name] = instruction

            if isinstance(instruction, config_instruction):
                config[instruction.key] = instruction

    if children:
        for name, instr in child_instruction.instructions(
                aspect, children).items():
            if name in instructions:
                instr = instr.compose(instructions[name])
            instructions[name] = instr

    aspectkws = config
    if aspectkws:
        @plumb
        def __init__(_next, self, *args, **kw):
            for k in kw.keys():
                if k not in aspectkws:
                    continue
                value = kw.pop(k)
                akw = aspectkws[k]
                if value is not akw.item:
                    setattr(self, akw.name, value)
            _next(*args, **kw)

        __init__.name = '__init__'
        __init__.parent = aspect
        if '__init__' in instructions:
            __init__ = __init__.compose(instructions['__init__'])
        instructions['__init__'] = __init__

    return (config, instructions)


def configured_aspect(aspect, cfg):
    unknown = set(cfg.keys()) - set(aspect.__metachao_config__.keys())
    if unknown:
        raise UnknownConfigKeys(tuple(unknown))

    name = aspect.__name__ + "_configured"
    bases = (aspect,)
    dct = dict()

    for k, v in cfg.items():
        instr = config_instruction(v)
        instr._key = k
        instr.name = aspect.__metachao_config__[k].name
        dct[instr.name] = instr

    configured = aspect.__class__(name, bases, dct)
    return configured


class AspectMeta(type):
    """meta class for aspects
    """
    def __call__(aspect, origin=_UNSET, **kw):
        if kw.pop('pdb', None):
            import pdb
            pdb.set_trace()
        elif kw.pop('ipdb', None):
            import ipdb
            ipdb.set_trace()

        if kw:
            aspect = configured_aspect(aspect, kw)

        if origin is _UNSET:
            return aspect

        if origin is None:
            raise ValueError("Need aspect, class, or instance, not %r!"
                             % (origin,))

        # if called with another aspect compose them
        if type(origin) is AspectMeta:
            return compose(aspect, origin)

        # a single aspects called on a normal class or an instance
        workbench = Workbench(origin)
        for instruction in aspect.__metachao_instructions__.values():
            instruction(workbench)

        # build a new class, with the same name and bases as the
        # target class, but a new dictionary with the aspect applied.
        # XXX: name is length limited... hackup traceback or something
        # to generate more useful info
        #name = '%s:%s' % (aspect.__name__, workbench.name)
        name = workbench.name
        workbench.dct['__metachao_aspects__'].insert(0, aspect)
        cls = workbench.type(name, workbench.baseclasses, workbench.dct)
        if ZOPE_INTERFACE_AVAILABLE:
            classImplements(cls, *tuple(implementedBy(aspect)))
        if utils.isclass(origin):
            cls.__metachao_class__ = cls
            return cls
        return cls()

    def __init__(aspect, name, bases, dct):
        """Will be called when a aspect class is created

        Parse the aspects dictionary and generate instructions from it.
        Undecorated attributes are understood as finalize instructions.

        >>> class P(Aspect):
        ...     a = Instruction(1)
        ...     b = 2
        >>> Instructions(P)
        [('a', <class 'metachao._instructions.Instruction'>, 1),
         ('b', <class 'metachao._instructions.overwrite'>, 2)]
        """
        super(AspectMeta, aspect).__init__(name, bases, dct)

        # Get the aspect's config and instructions
        (aspect.__metachao_config__,
         aspect.__metachao_instructions__) = parse_aspect(aspect)

        # # An existing docstring is an implicit plumb instruction for __doc__
        # if aspect.__doc__ is not None:
        #     instructions.append(plumb(aspect.__doc__, name='__doc__'))


class Aspect(object):
    """base class for aspects, just to set the metaclass
    """
    __metaclass__ = AspectMeta
