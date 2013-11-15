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


class instantiate(aspect.Aspect):
    """Self-instantiating class trees of dictionary-like nodes

When used on classes with metaclass `node`, it takes care of using the
tree of classes on the class and returns their on-demand created
instances.

saves the created instances in a dictionary in CLASSTREE_ATTR on the
instance.
    """
    # __metaclass__ = node
    @aspect.plumb
    def __init__(_next, self, *args, **kwargs):
        setattr(self, CLASSTREE_ATTR, dict())
        _next(*args, **kwargs)

    @aspect.plumb
    def __getitem__(_next, self, key):
        """Return an instance if it has been set in the classtree.

Instances are saved in the CLASSTREE_ATTR on the instance. Returns
either
1. an already created instance from this attribute
2. a new instance if a class has been provided with the classtree
3. the result of __getitem__ on the original class

instead of just a classname, the classtree can also hold a tuple,
where the first item is a class name and the rest are attributes of
the instance, which are used as parameters for creating the instance.
        """

        try:
            return getattr(self, CLASSTREE_ATTR)[key]
        except KeyError:
            pass

        try:
            cls = self.__class__[key]
            if isinstance(cls, tuple):
                params = (getattr(self, p) for p in cls[1:])
                cls = cls[0]
            else:
                params = ()

            node = cls(*params)
            getattr(self, CLASSTREE_ATTR)[key] = node
            return node
        except KeyError:
            pass

        return _next(key)
