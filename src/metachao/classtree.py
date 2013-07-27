try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


CLASSTREE_ATTR = '__metachao_classtree__'


def tree(cls):
    return getattr(cls, CLASSTREE_ATTR)


class node(type):
    """Class node

    Using this metaclass you can build trees consisting of classes.

    """
    def __init__(cls, name, bases, dct):
        super(node, cls).__init__(name, bases, dct)
        setattr(cls, CLASSTREE_ATTR, OrderedDict())

    def __delitem__(cls, key):
        del tree(cls)[key]

    def __getitem__(cls, key):
        return tree(cls)[key]

    def __setitem__(cls, key, value):
        tree(cls)[key] = value

    def __iter__(cls):
        return iter(tree(cls))

    def iterkeys(cls):
        return tree(cls).iterkeys()

    def itervalues(cls):
        return tree(cls).itervalues()

    def iteritems(cls):
        return tree(cls).iteritems()

    def keys(cls):
        return tree(cls).keys()

    def values(cls):
        return tree(cls).values()

    def items(cls):
        return tree(cls).items()


class Node(object):
    __metaclass__ = node
