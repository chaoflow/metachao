import types


# stolen from python's inspect and extended to handle metaclasses
def getmembers(object, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    results = []
    for key in dir(object):
        try:
            value = getattr(object, key)
        except AttributeError:
            # you are doing weird stuff, like applying aspects to metaclasses
            # good job!
            continue
        if not predicate or predicate(value):
            results.append((key, value))
    results.sort()
    return results


def isclass(obj):
    """Check whether an object is a regular class

    inspect.isclass uses:
    return isinstance(object, types.ClassType) or hasattr(object, '__bases__')

    If a getattr is broken, the latter test falsly returns True.
    """
    return type(obj) in (types.ClassType, type)
