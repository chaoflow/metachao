import logging
import utils

from inspect import getmembers

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('metachao')


class Instruction(object):
    name = None
    parent = None

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

    # def __eq__(self, right):
    #     """Instructions are equal if ...

    #     - they are the very same
    #     - their class is the very same and their payloads are equal
    #     """
    #     if self is right:
    #         return True
    #     if not self.__class__ is right.__class__:
    #         return False
    #     if self.name != right.name or self.payload != right.payload:
    #         return False
    #     return True

    def __init__(self, item, name=None):
        """
            >>> class Foo: pass
            >>> Instruction(Foo).item is Foo
            True
            >>> Instruction(Foo).name is None
            True
            >>> Instruction(Foo, name='foo').name == 'foo'
            True

            The name can be provided here for easier testing
        """
        self.item = item
        if name is not None:
            self.name = name

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

    def compose(self, other):
        # XXX: we probably should log warning when overwriting a
        # plumbing - unlikely that somebody constructs a plumbing and
        # then overwrites it
        if isinstance(self, default):
            return other
        else:
            return self


class default(EitherOrInstruction):
    def check(self, workbench, effective):
        for x in getmembers(workbench.origin):
            if self.name == x[0]:
                return False
        else:
            return True


# XXX: should probably be inheriting from overwrite
class config(default):
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


class wraps(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __call__(self, wrapper):
        wrapped = self.wrapped
        wrapper.__doc__ = wrapped.__doc__
        wrapper.__module__ = getattr(wrapped, '__module__', 'probably_builtin')
        wrapper.__name__ = wrapped.__name__
        return wrapper


class plumb(Instruction):
    @property
    def function_list(self):
        function_list = self.payload
        if not type(function_list) in (tuple, list):
            function_list = (function_list,)
        return tuple(function_list)

    def apply(self, workbench, effective):
        function_list = list(self.function_list)

        # If the last function is a default or overwrite instruction,
        # we pop it off and later evaluate its usage versus a function
        # retrieved from the origin. If origin is an instance, this
        # function builds the bridge to it and therefore needs to be
        # bound to it.
        instr = None
        if isinstance(function_list[-1], (default, overwrite)):
            instr = function_list.pop()
            fn = instr.payload
            if not utils.isclass(workbench.origin):
                fn = fn.__get__(workbench.origin, workbench.origin.__class__)

        # overwrite wins over origin, default loses
        if isinstance(instr, overwrite):
            _next_method = fn
        else:
            try:
                _next_method = getattr(workbench.origin, self.name)
            except AttributeError:
                if isinstance(instr, default):
                    _next_method = fn
                else:
                    raise

        # nest remaining functions
        for i, fn in enumerate(reversed(function_list)):
            _next_is_bound = (i == 0) and not utils.isclass(workbench.origin)
            _next_method = self._wrap(workbench.origin, fn,
                                      _next_method, _next_is_bound)

        # set wrapper
        workbench.dct[self.name] = _next_method
        return True

    def compose(self, other):
        if isinstance(other, plumb):
            instr = plumb(self.function_list + other.function_list)
        elif isinstance(other, (default, overwrite)):
            instr = plumb(self.function_list + (other,))
        else:
            raise CantTouchThis
        instr.name = self.name
        return instr

    def _wrap(self, origin, fn, _next_method, _next_is_bound):
        attrname = self.name

        @wraps(fn)
        def wrapper(self, *args, **kw):
            __traceback_info__ = attrname

            @wraps(_next_method)
            def _next(*args, **kw):
                if _next_is_bound:
                    return _next_method(*args, **kw)
                else:
                    return _next_method(self, *args, **kw)

            # All _next methods, not just for the current name,
            # are available via _next.all
            _next.all = AllNext(origin, self)
            _next._next_method = _next_method
            return fn(_next, self, *args, **kw)

        return wrapper


class child(object):
    @classmethod
    def instructions(cls, aspect, children):
        instructions = dict()

        if not children:
            return instructions

        @plumb
        def __getitem__(_next, self, key):
            """Consult getter for known child or call _next
            """
            try:
                child = children[key]
                getter = child._fns['getter'].__get__(self, self.__class__)
            except (AttributeError, KeyError):
                getter = _next
            return getter(key)

        __getitem__.name = '__getitem__'
        __getitem__.parent = aspect
        instructions['__getitem__'] = __getitem__

        @plumb
        def __setitem__(_next, self, key, value):
            """Consult setter for known child or call _next
            """
            try:
                child = children[key]
                setter = child._fns['setter'].__get__(self, self.__class__)
            except (AttributeError, KeyError):
                setter = _next
            return setter(key, value)

        __setitem__.name = '__setitem__'
        __setitem__.parent = aspect
        instructions['__setitem__'] = __setitem__

        @plumb
        def __delitem__(_next, self, key):
            """Consult deleter for known child or call _next
            """
            try:
                child = children[key]
                deleter = child._fns['deleter'].__get__(self, self.__class__)
            except (AttributeError, KeyError):
                deleter = _next
            return deleter(key)

        __delitem__.name = '__delitem__'
        __delitem__.parent = aspect
        instructions['__delitem__'] = __delitem__

        return instructions

    def __init__(self, getter=None, setter=None, deleter=None, key=None):
        self._fns = dict()
        if getter is not None:
            self._fns['getter'] = getter
        if setter is not None:
            self._fns['setter'] = setter
        if deleter is not None:
            self._fns['deleter'] = deleter
        if key is not None:
            self.key = key

    def __call__(self, getter=None, setter=None, deleter=None, key=None):
        if getter is not None:
            self._fns['getter'] = getter
        if setter is not None:
            self._fns['setter'] = setter
        if deleter is not None:
            self._fns['deleter'] = deleter
        if key is not None:
            self.key = key
        return self

    def getter(self, getter):
        self._fns['getter'] = getter
        return self

    def setter(self, setter):
        self._fns['setter'] = setter
        return self

    def deleter(self, deleter):
        self._fns['deleter'] = deleter
        return self
