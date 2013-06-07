from inspect import getmembers


def derive(prototype, bind=dict()):
    Prototyper = prototyper(prototype, bind=bind)
    derived = Prototyper()
    return derived


def prototyper(prototype, bind=dict()):
    class Prototyper(prototype.__class__, object):
        def __init__(self, *args, **kw):
            prototype.__class__.__init__(self, *args, **kw)
            self.__metachao_prototype__ = prototype
            self.__metachao_bind__ = dict(getattr(prototype,
                                                  '__metachao_bind__',
                                                  ()))
            self.__metachao_bind__.update(bind)

        def __getattribute__(self, name):
            """realize prototyping chain

            1. instance dictionary
            2. for callables/properties check instance's class
               (the ad-hoc Prototyper)
            3. get attribute from prototype
            """
            # shortcut for things we don't want to go into the prototype chain
            if name in (
                '__class__',
                '__dict__',
                '__metachao_bind__',
                '__metachao_prototype__',
            ):
                return object.__getattribute__(self, name)

            # no binding, if served from instance dictionary
            selfdict = self.__dict__
            if name in selfdict:
                return selfdict[name]

            # check class' members for properties
            attr = dict((k, v) for k, v in getmembers(self.__class__)
                        if k == name and isinstance(v, property)
                        ).get(name, ())

            # enter prototype chain
            if attr is ():
                prototype = self.__metachao_prototype__
                attr = getattr(prototype, name)

            # get to real function in case of methods
            attr = getattr(attr, 'im_func', attr)

            # bind descriptors to instance or whatever they are supposed to
            # bind to
            if hasattr(attr, '__get__'):
                bindto = self.__metachao_bind__.get(name)
                if bindto is None:
                    bindto = self
                attr = attr.__get__(bindto, bindto.__class__)

            return attr

    return Prototyper


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
