import functools as ft
import types


def boundproperty(instance, name):
    """Return a property with fget/fset/fdel bound to instance
    """
    return property(
        lambda self: getattr(instance, name),
        lambda self, value: setattr(instance, name, value),
        lambda self: delattr(instance, name),
        )


# XXX: do we need this or is lowercase partial sufficient?
class Partial(object):
    def __init__(self, payload, **kw):
        self.payload = payload
        self.default_kw = kw

    def __call__(self, *args, **kw):
        return self.payload(*args, **dict(chain(self.default_kw.iteritems(),
                                                kw.iteritems())))


class partial(ft.partial):
    """
        >>> class A(object):
        ...     p = partial(lambda x, self, y: x * y, 2)
        >>> A().p(2)
        4
    """
    def __get__(self, obj, objtype=None):
        """Simulate func_descr_get() in Objects/funcobject.c
        """
        return types.MethodType(self, obj, objtype)


def searchnameinbases(name, bases):
    """
        >>> class A(object):
        ...     foo = 1

        >>> class B(A):
        ...     pass

        >>> searchnameinbases('foo', (B,))
        True
        >>> searchnameinbases('bar', (B,))
        False
    """
    for base in bases:
        if name in base.__dict__:
            return True
        if searchnameinbases(name, base.__bases__):
            return True
    return False


class Bases(object):
    """Used to search in base classes for attributes
    """
    def __init__(self, *bases):
        self.bases = bases

    def __contains__(self, name):
        return searchnameinbases(name, self.bases)
