from abc import ABCMeta
from inspect import getmembers, getmro

try:
    from zope.interface import classImplements
    from zope.interface import implementedBy
    ZOPE_INTERFACE_AVAILABLE = True
except ImportError:                   #pragma NO COVERAGE
    ZOPE_INTERFACE_AVAILABLE = False  #pragma NO COVERAGE


from metachao._instructions import Instruction
from metachao._instructions import aspectkw
from metachao._instructions import overwrite
from metachao._instructions import plumb
from metachao.prototype import prototype_property
from metachao.tools import Bases, Partial, boundproperty
from metachao import utils


DICT_KEYS_OF_PLAIN_CLASS = ['__dict__', '__doc__', '__module__', '__weakref__']


class Workbench(object):
    def __init__(self, origin, **kw):
        self.origin = origin
        self.kw = kw
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
            self.dct['__init__'] = lambda *a, **kw : None
            self.dct['__metachao_prototype__'] = origin

        if '__metachao_effective__' in origin.__dict__:
            self.dct['__metachao_effective__'] = \
                origin.__metachao_effective__.copy()


class _UNSET(object):
    pass


class AspectMeta(ABCMeta):
    """meta class for aspects
    """
    def __call__(aspect, origin=_UNSET, **kw):
        if kw.get('pdb'):
            import pdb;pdb.set_trace()
        elif kw.get('ipdb'):
            import ipdb;ipdb.set_trace()

        # if called without positional arg, return partially applied
        # aspect
        if origin is _UNSET:
            if not kw:
                raise NeedKw
            # XXX: this does not play nice with ABC
            # XXX: return an aspect that is differently configured
            return Partial(aspect, **kw)

        if origin is None:
            raise ValueError(
                "Need aspect, class, or instance, not %r!" % (origin,))

        # if called with another aspect compose them
        if type(origin) is AspectMeta:
            if kw:
                raise Unsupported("kw and composition not supported")
            name = "AspectComposition"
            aspects = []
            for asp in (aspect, origin):
                if hasattr(asp, '__metachao_compose__'):
                    aspects.extend(asp.__metachao_compose__)
                else:
                    aspects.append(asp)
            composite = AspectMeta(name, (Aspect,), dict(__metachao_compose__=aspects))
            #type(origin).register(origin, composite)
            #type(aspect).register(aspect, composite)
            return composite

        # if composition, chain them
        if hasattr(aspect, '__metachao_compose__'):
            for asp in reversed(aspect.__metachao_compose__):
                origin = asp(origin, **kw)
            # if type(origin) is type:
            #     type(aspect).register(aspect, origin)
            return origin

        # a single aspects called on a normal class or an instance
        workbench = Workbench(origin, **kw)
        for instruction in aspect.__metachao_instructions__.values():
            instruction(workbench)

            #raise AspectCollision(instr.name, aspect, target)

            # in case of instances functions need to be bound
            # if not x_is_class and (type(instr) is types.FunctionType):
            #     instr = instr.__get__(x)

        # build a new class, with the same name and bases as the
        # target class, but a new dictionary with the aspect applied.
        # XXX: name is lenght limited... hackup traceback or something
        # to generate more useful info
        #name = '%s:%s' % (aspect.__name__, workbench.name)
        name = workbench.name
        workbench.dct['__metachao_aspects__'].insert(0, aspect)
        cls = workbench.type(name, workbench.baseclasses, workbench.dct)
        #type(aspect).register(aspect, cls)
        if ZOPE_INTERFACE_AVAILABLE:
            classImplements(cls, *tuple(implementedBy(aspect)))
        if utils.isclass(origin):
            if type(cls) is AspectMeta and kw:
                raise OldCodePath
                return Partial(cls, **kw)
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

        # Get the aspect's instructions list
        instructions = aspect.__metachao_instructions__ = dict()

        # walk the mro, w/o object, gathering/creating instructions
        # XXX: not sure whether that is good
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
                    ): continue
                if name in DICT_KEYS_OF_PLAIN_CLASS:
                    continue
                if name in instructions:
                    continue

                # undecorated items are understood as overwrite
                if isinstance(item, Instruction):
                    instruction = item
                else:
                    instruction = overwrite(item)

                instruction.name = name
                instruction.parent = cls
                instructions[name] = instruction

        # for (every) aspectkw we need to plumb __init__
        aspectkws = dict([(x.key, x) for x in instructions.values()
                          if isinstance(x, aspectkw)])
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
            instructions['__init__'] = __init__

        # # An existing docstring is an implicit plumb instruction for __doc__
        # if aspect.__doc__ is not None:
        #     instructions.append(plumb(aspect.__doc__, name='__doc__'))

        # # XXX: introduce C3 resolution
        # # check our bases for instructions we don't have already and which
        # # are not overwritten by our instructions (stage1)
        # for base in bases:
        #     # XXX: I don't like this code
        #     for instr in Instructions(base):
        #         # skip instructions we have already
        #         if instr in instructions:
        #             continue
        #         # stage1 instructions with the same name are ignored
        #         if instr.__name__ in [x.__name__ for x in instructions if
        #                 x.__stage__ == 'stage1']:
        #             continue
        #         instructions.append(instr)


class Aspect(object):
    """base class for aspects, just to set the metaclass
    """
    __metaclass__ = AspectMeta
