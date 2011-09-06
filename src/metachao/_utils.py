from metachao.aspect import Aspect


def compose(*args, **kw):
    x = args[0]
    xs = args[1:]
    if not xs:
        return curry(x, **kw) if kw else x
    if not issubclass(x, Aspect):
        raise Exception("All except last need to be aspects.")
    return x(compose(*xs), **kw)
