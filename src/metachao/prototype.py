from inspect import getmembers


def bound_property(prop, name):
    name = '__metachao_bind_%s__' % name
    def fget(self):
        bindto = getattr(self, name, None)
        return prop.fget(bindto is not None and bindto or self)
    def fset(self, value):
        bindto = getattr(self, name, None)
        return prop.fset(bindto is not None and bindto or self, value)
    def fdel(self):
        bindto = getattr(self, name, None)
        return prop.fdel(bindto is not None and bindto or self)
    return property(fget, fset, fdel, prop.__doc__)


def prototyper__getattr__(self, name):
    attr = getattr(self.__metachao_prototype__, name)
    if callable(attr) and not name in self.__metachao_bound_methods__:
        attr = attr.im_func.__get__(self, self.__class__)
    return attr


def derive(prototype, bind=None):
    bound_methods =  set(
        getattr(prototype, '__metachao_bound_methods__', set())
        )
    dct = {
        '__getattr__': prototyper__getattr__,
        '__metachao_bound_methods__': bound_methods,
        '__metachao_prototype__': prototype,
        }

    # all these need to be bound, once we are done
    to_bind = bind is not None and bind.keys() or []

    for name, attr in getmembers(prototype.__class__):
        # properties need to be put in our class' dict anyway,
        # independent of whether bound or not
        if type(attr) is property:
            if name in to_bind:
                slot = '__metachao_bind_%s__' % name
                dct[slot] = bind[name]
                if not hasattr(prototype, slot):
                    attr = bound_property(attr, name)
                to_bind.remove(name)
            dct[name] = attr
        # methods are only put into our class' dict, if they are to be
        # bound to something else than our instance
        elif name in to_bind:
            attr = attr.__get__(bind[name], bind[name].__class__)
            dct[name] = attr
            to_bind.remove(name)
            bound_methods.add(name)

    # search for the remaining methods to be bound. properties can't
    # be left now, because they would have been found via the
    # immediate prototype above
    for name in to_bind:
        attr = getattr(prototype, name)
        attr = attr.im_func.__get__(bind[name], bind[name].__class__)
        dct[name] = attr
        bound_methods.add(name)

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
