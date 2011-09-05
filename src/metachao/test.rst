Aspect base class::

    >>> from metachao import Aspect

Two aspects used on class A::

    >>> class f(Aspect):
    ...     a = 1
    >>> class g(Aspect):
    ...     b = 2

    >>> class Base(object):
    ...     b = 3

    >>> @f
    ... @g
    ... class C(Base):
    ...     c = 3

    >>> C.a
    1
    >>> C.b
    2
    >>> C.c
    3

    >>> c = C()
    >>> c.a
    1
    >>> c.b
    2
    >>> c.c
    3

.. different syntax::

..     >>> @f(g)
..     ... class C(object):
..     ...     c = 3

..     >>> C.a
..     1
..     >>> C.b
..     2
..     >>> C.c
..     3

..     >>> c = C()
..     >>> c.a
..     1
..     >>> c.b
..     2
..     >>> c.c
..     3

.. different syntax::

..     >>> from metachao import compose

..     >>> @compose(f, g)
..     ... class C(object):
..     ...     c = 3

..     >>> C.a
..     1
..     >>> C.b
..     2
..     >>> C.c
..     3

..     >>> c = C()
..     >>> c.a
..     1
..     >>> c.b
..     2
..     >>> c.c
..     3

Collision::

    >>> class f(Aspect):
    ...     a = 1

    >>> @f
    ... class C(object):
    ...     a = 2
    Traceback (most recent call last):
      ...
    AspectCollision: a

XXX: py.test not nice: __main__.f, instead of just f

default instruction::

    >>> from metachao import default
    >>> class f(Aspect):
    ...     a = default(1)
    ...     b = default(1)
    ...     c = default(1)

    >>> class Base(object):
    ...     b = 2

    >>> @f
    ... class A(Base):
    ...     c = 3

    >>> A.a
    1
    >>> A.b
    2
    >>> A.c
    3

overwrite instruction::

    >>> from metachao import overwrite
    >>> class f(Aspect):
    ...     a = overwrite(1)
    ...     b = overwrite(1)
    ...     c = overwrite(1)

    >>> class g(Aspect):
    ...     c = overwrite(2)

    >>> class Base(object):
    ...     b = 3

    >>> @f
    ... @g
    ... class C(Base):
    ...     a = 4

    >>> C.a
    4
    >>> C.b
    1
    >>> C.c
    1

finalize instruction::

    >>> from metachao import finalize
    >>> class f(Aspect):
    ...     a = finalize(1)

    >>> class g(Aspect):
    ...     a = overwrite(2)

    >>> @f
    ... @g
    ... class C(object):
    ...     pass

    >>> C.a
    1

plumb instruction::

    .. >>> from metachao import plumb
    .. >>> class f(Aspect):
    .. ...     @plumb
    .. ...     def func(_next, self):
    .. ...         return 2 * _next()

    .. >>> @f
    .. ... class C(object):
    .. ...     def func(self):
    .. ...         return 3

    .. >>> c = C()
    .. >>> c.func()
    .. 6


``zope.interface`` (if available)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aspects do not depend on ``zope.interface`` but are aware of it. If
``zope.interface`` is available, they will declare their interfaces
on the plumbing::

    >>> from zope.interface import Interface
    >>> from zope.interface import implements

An aspect with a base class that also implements an interface::

    >>> class ISomeBase(Interface):
    ...     pass

    >>> class ISome(Interface):
    ...     pass

    >>> class gbase(Aspect):
    ...     implements(ISomeBase)

    >>> class g(gbase):
    ...     implements(ISome)

    >>> ISomeBase.implementedBy(gbase)
    True
    >>> ISome.implementedBy(g)
    True

A class using aspect ``g``and implementing ``IC``::

    >>> class IC(Interface):
    ...     pass

    >>> @g
    ... class Class(object):
    ...     implements(IC)

The directly declared interface is implemented::

    >>> IC.implementedBy(Class)
    True

The interfaces implemented by the aspect and its base are also implemented::

    >>> ISome.implementedBy(Class)
    True
    >>> ISomeBase.implementedBy(Class)
    True
