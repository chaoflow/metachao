from itertools import chain

try:
    from zope.interface import classImplements
    from zope.interface import implementedBy
    ZOPE_INTERFACE_AVAILABLE = True
except ImportError:                   # pragma NO COVERAGE
    ZOPE_INTERFACE_AVAILABLE = False  # pragma NO COVERAGE

from metachao._instructions import Instruction
from metachao._instructions import finalize
from metachao.exceptions import AspectCollision
from metachao.tools import Bases


# XXX: derive from list/UserList and store self on aspect
class Instructions(object):
    """Adapter to store instructions on a aspect

    >>> class P(object): pass
    >>> instrs = Instructions(P)
    >>> instrs.append(1)
    >>> instrs.instructions
    [1]
    >>> instrs = Instructions(P)
    >>> instrs.instructions
    [1]
    """
    attrname = "__metachao_instructions__"

    @property
    def instructions(self):
        return getattr(self.aspect, self.attrname)

    def __call__(self, workbench):
        if type(workbench.origin) is AspectMeta:
            # XXX: it is an error if there is no __metachao_instructions__ yet
            workbench.dct.setdefault(self.attrname, []).extend(self)
        else:
            for instr in self.instructions:
                instr(workbench)

    def __getattr__(self, name):
        return getattr(self.instructions, name)

    # XXX: needed explicitly to make it iterable?
    def __iter__(self):
        return self.instructions.__iter__()

    def __init__(self, aspect):
        self.aspect = aspect
        if self.attrname not in aspect.__dict__:
            setattr(aspect, self.attrname, [])

    def __repr__(self):
        return repr(
            [(x.name, x.__class__, x.payload) for x in self.instructions]
            )


class Partial(object):
    def __init__(self, payload, **kw):
        self.payload = payload
        self.default_kw = kw

    def __call__(self, *args, **kw):
        return self.payload(*args, **dict(chain(self.default_kw.iteritems(),
                                                kw.iteritems())))


class Workbench(object):
    def __init__(self, origin, **kw):
        self.origin = origin
        self.kw = kw
        self.dct = origin.__dict__.copy()
        self.bases = Bases(origin)


class AspectMeta(type):
    """meta class for aspects
    """
    def __call__(aspect, origin=None, *args, **kw):
        if origin is None:
            # return partially applied aspect
            if not kw:
                raise NeedKw
            # XXX: support for partial args application?
            return Partial(aspect, **kw)

        workbench = Workbench(origin, **kw)
        Instructions(aspect)(workbench)

            #raise AspectCollision(instr.name, aspect, target)

            # in case of instances functions need to be bound
            # if not x_is_class and (type(instr) is types.FunctionType):
            #     instr = instr.__get__(x)

        # build a new class, with the same name and bases as the
        # target class, but a new dictionary with the aspect applied.
        cls = type(origin)(origin.__name__, origin.__bases__, workbench.dct)
        if ZOPE_INTERFACE_AVAILABLE:
            classImplements(cls, *tuple(implementedBy(aspect)))
        return cls

    def __init__(aspect, name, bases, dct):
        """Will be called when a aspect class is created

        Parse the aspects dictionary and generate instructions from it.
        Undecorated attributes are understood as finalize instructions.

        >>> class P(Aspect):
        ...     a = Instruction(1)
        ...     b = 2
        >>> Instructions(P)
        [('a', <class 'metachao._instructions.Instruction'>, 1),
         ('b', <class 'metachao._instructions.finalize'>, 2)]
        """
        super(AspectMeta, aspect).__init__(name, bases, dct)

        # Get the aspect's instructions list
        instructions = Instructions(aspect)

        for name, item in aspect.__dict__.iteritems():
            # ignored attributes
            if name.startswith('__metachao_'):
                continue
            if name in ['__doc__', '__module__']:
                continue

            # XXX: rethink this
            # undecorated items are understood as finalize
            if not isinstance(item, Instruction):
                item = finalize(item)
            item.__name__ = name
            item.__parent__ = aspect
            instructions.append(item)

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
