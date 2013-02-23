from inspect import getmembers


def __getattr__(self, name):
    attr = getattr(self.__metachao_prototype__, name)
    if callable(attr):
        attr = attr.im_func.__get__(self, self.__class__)
    return attr


def derive(prototype, **kw):
    name = "Prototyper"
    bases = ()
    dct = {
        '__getattr__': __getattr__,
        '__metachao_prototype__': prototype,
        }
    dct.update((k,v) for k,v in getmembers(prototype.__class__)
               if type(v) is property)
    Prototyper = type(name, bases, dct)
    derived = Prototyper()
    return derived


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
