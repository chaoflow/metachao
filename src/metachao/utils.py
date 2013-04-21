import types


def isclass(obj):
    """Check whether an object is a regular class

    inspect.isclass uses:
    return isinstance(object, types.ClassType) or hasattr(object, '__bases__')

    If a getattr is broken, the latter test falsly returns True.
    """
    return type(obj) in (types.ClassType, type)
