import logging

from functools import wraps
from inspect import getmembers
from inspect import getmro
from inspect import isclass

from metachao.exceptions import AspectCollision
from metachao.tools import partial

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('metachao')


def payload(item):
    """Get to the payload through a chain of instructions

        >>> class Foo: pass
        >>> payload(Instruction(Instruction(Foo))) is Foo
        True
    """
    # XXX: check in what case this is needed
    while isinstance(item, Instruction):
        item = item.item
    return item


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
        return payload(self)

    def apply(self, workbench, effective):
        """apply the instruction

        May raise exceptions:
        - AspectCollision

        return True (applied) / False (not applied)
        """
        raise NotImplementedError  # pragma NO COVERAGE

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
        raise NotImplementedError  # pragma NO COVERAGE

    def value(self, workbench):
        return self.payload


class default(EitherOrInstruction):
    def check(self, workbench, effective):
        return self.name not in (x[0] for x in getmembers(workbench.origin))


class finalize(EitherOrInstruction):
    def check(self, workbench, effective):
        if self.name not in workbench.dct:
            return True
        if effective.get(self.name) is None or \
                isinstance(effective.get(self.name), finalize):
            raise AspectCollision("%s\n  %s\n  with: %s" % (
                self.name, workbench.dct[self.name], self.__parent__))
        return True


class aspectkw(finalize):
    """define a kw for the aspect
    """
    def __init__(self, **kw):
        if len(kw) != 1:
            raise NeedExactlyOneKeyword
        # finalize.apply will use item
        self.item = kw.values()[0]
        self.key = kw.keys()[0]

    def value(self, workbench):
        if self.key in workbench.kw:
            return workbench.kw[self.key]
        return self.payload


class overwrite(EitherOrInstruction):
    def check(self, workbench, effective):
        if self.name not in workbench.dct:
            return True
        if effective.get(self.name) is None:
            return False
        if isinstance(effective.get(self.name), finalize):
            # XXX: should this be a collision? maybe things defined on
            # the plumbing itself should be only similar to finalize,
            # but not finalize.
            return False
        return True


class AllNext(object):
    """access to all _next methods
    """
    __instance = None

    def __init__(self, dct, instance=None):
        self.__dct = dct
        if instance is not None:
            self.__instance = instance

    def __getattribute__(self, name):
        """all attribute lookups are forwarded into the dct
        """
        dct = object.__getattribute__(self, '_AllNext__dct')
        instance = object.__getattribute__(self, '_AllNext__instance')
        try:
            attr = dct[name]
        except KeyError:
            raise AttributeError(name)
        if instance:
            attr = attr.__get__(instance, instance.__class__)
        return attr


class plumb(Instruction):
    def apply(self, workbench, effective):
        # find raw _next function
        try:
            _next = workbench.dct[self.name]
        except KeyError:
            if not isclass(workbench.origin):
                raise
            for base in getmro(workbench.origin)[1:]:
                try:
                    _next = base.__dict__[self.name]
                    break;
                except KeyError:
                    pass
            else:
                raise KeyError(self.name)
        try:
            _next.__get__
            needs_to_be_bound = True
        except AttributeError:
            needs_to_be_bound = False
        # create and set wrapper
        payload = self.payload
        if needs_to_be_bound:
            @wraps(payload)
            def wrapper(self, *args, **kw):
                boundnext = _next.__get__(self, self.__class__)
                def _nextall(*args2, **kw2):
                    return boundnext(*args2, **kw2)
                # All _next methods, not just for the current name,
                # are available via _next.all
                _nextall.all = AllNext(workbench.dct, self)
                return payload(_nextall, self, *args, **kw)
        else:
            @wraps(payload)
            def wrapper(self, *args, **kw):
                def _nextall(*args2, **kw2):
                    return _next(*args2, **kw2)
                # All _next methods, not just for the current name,
                # are available via _next.all
                _nextall.all = AllNext(workbench.dct)
                return payload(_nextall, self, *args, **kw)
        workbench.dct[self.name] = wrapper
        return True
