import logging

from functools import wraps
from inspect import getmembers
from inspect import getmro
from inspect import isclass

from metachao.tools import partial

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('metachao')


class Instruction(object):
    __name__ = None
    __parent__ = None

    @property
    def name(self):
        """Name of the attribute the instruction is for
        """
        return self.__name__

    @property
    def payload(self):
        item = self
        # XXX: check in what case this is needed
        while isinstance(item, Instruction):
            item = item.item
        return item

    def apply(self, workbench, effective):
        """apply the instruction

        May raise exceptions:
        - AspectCollision

        return True (applied) / False (not applied)
        """
        raise NotImplementedError  #pragma NO COVERAGE

    def __call__(self, workbench):
        # XXX: record keywords also with effective instructions?
        effective = workbench.dct.setdefault('__metachao_effective__', {})
        if self.apply(workbench, effective):
            log.debug('effective: %s', self)
            effective[self.name] = self

    def __eq__(self, right):
        """Instructions are equal if ...

        - they are the very same
        - their class is the very same and their payloads are equal
        """
        if self is right:
            return True
        if not self.__class__ is right.__class__:
            return False
        if self.name != right.name or self.payload != right.payload:
            return False
        return True

    def __init__(self, item, name=None):
        """
            >>> class Foo: pass
            >>> Instruction(Foo).item is Foo
            True
            >>> Instruction(Foo).__name__ is None
            True
            >>> Instruction(Foo, name='foo').__name__ == 'foo'
            True

            The name can be provided here for easier testing
        """
        self.item = item
        if name is not None:
            self.__name__ = name

    def __repr__(self):
        return "<%s '%s' %r>" % (self.__class__.__name__,
                                   self.name, self.payload)


class EitherOrInstruction(Instruction):
    """Instructions where either an existing value or the provided one is used
    """
    def apply(self, workbench, effective):
        if effective.get(self.name) is self:
            log.debug('skipping eitheror: %r', self)
            return False
        if self.check(workbench, effective):
            workbench.dct[self.name] = self.value(workbench)
        return True

    def check(self, workbench, effective):
        """Check whether to apply an instruction

        ``bases`` is a wrapper for all base classes of the plumbing and
        provides ``__contains__``, instructions may or may not need it.
        """
        raise NotImplementedError  #pragma NO COVERAGE

    def value(self, workbench):
        return self.payload


class default(EitherOrInstruction):
    def check(self, workbench, effective):
        for x in getmembers(workbench.origin):
            if self.name == x[0]:
                return False
        else:
            return True


class aspectkw(default):
    """define a kw for the aspect
    """
    _key = None

    @property
    def key(self):
        return self._key or self.name.strip('_')

    def __init__(self, *args, **kw):
        if len(kw) + len(args) != 1:
            raise NeedExactlyOneKeyword
        # default.apply will use item
        if kw:
            self.item = kw.values()[0]
            self._key = kw.keys()[0]
        else:
            self.item = args[0]

    def value(self, workbench):
        if self.key in workbench.kw:
            return workbench.kw[self.key]
        return self.payload
cfg = aspectkw


class overwrite(EitherOrInstruction):
    """Internal instruction for undecorated attributes
    """
    def check(self, workbench, effective):
        return True


class AllNext(object):
    """access to all _next methods
    """
    __instance = None

    def __init__(self, origin, instance=None):
        self.__origin = origin
        if instance is not None:
            self.__instance = instance

    def __getattribute__(self, name):
        """all attribute lookups are forwarded to origin
        """
        origin = object.__getattribute__(self, '_AllNext__origin')
        instance = object.__getattribute__(self, '_AllNext__instance')
        attr = getattr(origin, name)
        if instance:
            attr = attr.__get__(instance, instance.__class__)
        return attr


class plumb(Instruction):
    def apply(self, workbench, effective):
        payload = self.payload
        name = self.name
        _next_method = getattr(workbench.origin, self.name)
        if type(workbench.origin) is type:
            @wraps(payload)
            def wrapper(self, *args, **kw):
                __traceback_info__ = name
                def _next(*args, **kw):
                    return _next_method(self, *args, **kw)
                # All _next methods, not just for the current name,
                # are available via _next.all
                _next.all = AllNext(workbench.origin, self)
                return payload(_next, self, *args, **kw)
        else:
            @wraps(payload)
            def wrapper(self, *args, **kw):
                __traceback_info__ = name
                def _next(*args, **kw):
                    return _next_method(*args, **kw)
                # All _next methods, not just for the current name,
                # are available via _next.all
                _next.all = AllNext(workbench.origin)
                return payload(_next, self, *args, **kw)

        # set wrapper
        workbench.dct[self.name] = wrapper
        return True
