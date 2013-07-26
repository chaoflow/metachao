try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


FACTORY_ATTR = '__metachao_classnode_factories__'


def factories(cls):
    return getattr(cls, FACTORY_ATTR)


class classnode(type):
    """Class node

    Using this metaclass you can build trees consisting of classes.

    """
    def __init__(cls, name, bases, dct):
        super(classnode, cls).__init__(name, bases, dct)
        setattr(cls, FACTORY_ATTR, OrderedDict())

    def __delitem__(cls, key):
        del factories(cls)[key]

    def __getitem__(cls, key):
        return factories(cls)[key]

    def __setitem__(cls, key, value):
        factories(cls)[key] = value

    def __iter__(cls):
        return iter(factories(cls))

    def iterkeys(cls):
        return factories(cls).iterkeys()

    def itervalues(cls):
        return factories(cls).itervalues()

    def iteritems(cls):
        return factories(cls).iteritems()

    def keys(cls):
        return factories(cls).keys()

    def values(cls):
        return factories(cls).values()

    def items(cls):
        return factories(cls).items()


class ClassNode(object):
    __metaclass__ = classnode
