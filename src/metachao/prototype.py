from inspect import getmembers


class boundproperty(property):
    def __init__(self, prop, name):
        name = '__metachao_bind_%s__' % name
        def bound_fget(self):
            bindto = getattr(self, name, None)
            return prop.fget(bindto is not None and bindto or self)
        def bound_fset(self, value):
            bindto = getattr(self, name, None)
            return prop.fset(bindto is not None and bindto or self, value)
        def bound_fdel(self):
            bindto = getattr(self, name, None)
            return prop.fdel(bindto is not None and bindto or self)
        property.__init__(self, bound_fget, bound_fset, bound_fdel, prop.__doc__)


def prototyper__getattr__(self, name):
    attr = getattr(self.__metachao_prototype__, name)
    if callable(attr):
        bindto = getattr(self, '__metachao_bind_%s__' % (name,), None)
        if bindto is None:
            bindto = self
        attr = attr.im_func.__get__(bindto, bindto.__class__)
    return attr


def derive(prototype, bind=None):
    dct = {
        '__getattr__': prototyper__getattr__,
        '__metachao_prototype__': prototype,
        }

    for name in bind or ():
        dct['__metachao_bind_%s__' % name] = bind[name]

    for name, attr in getmembers(prototype.__class__):
        if isinstance(attr, property):
            if not isinstance(attr, boundproperty):
                attr = boundproperty(attr, name)
            dct[name] = attr

    name = "Prototyper"
    bases = ()
    Prototyper = type(name, bases, dct)
    derived = Prototyper()
    return derived


# XXX: I don't think this will be needed anymore
def prototype_property(prototype, prop):
    """prototype property

    - try fget on self, fallback to prototype
    - fset and fdel on self
    """
    def fget(self):
        try:
            return prop.fget(self)
        except AttributeError:
            return prop.fget(prototype)
    return property(fget, prop.fset, prop.fdel, prop.__doc__)
