try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from metachao import aspect


CLASSTREE_ATTR = '__metachao_classtree__'


def tree(cls):
    """Get the class tree of a class
    """
    return getattr(cls, CLASSTREE_ATTR)


class node(type):
    """Generate classtree node's

    A class tree consists of classes (in contrast to instances) that
    can store children via dictionary API.

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


class instantiate_upon_traversal(aspect.Aspect):
    """Instantiate class trees of dictionary-like nodes upon traversal"""

    @aspect.plumb
    def __getitem__(_next, self, key):
        try:
            return _next(key)
        except KeyError:
            pass

        node = self.__class__[key]()
        self[key] = node
        return node


class Base(object):
    """Base class for class-based trees
    """
    __metaclass__ = node


@instantiate_upon_traversal
class Node(Base, OrderedDict):
    pass
