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
