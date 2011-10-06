Aspect base class::

    >>> from metachao.aspect import Aspect

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

    .. >>> class f(Aspect):
    .. ...     a = 1

    .. >>> @f
    .. ... class C(object):
    .. ...     a = 2
    .. Traceback (most recent call last):
    ..   ...
    .. AspectCollision: a
    ..   2
    ..   with: <class 'f'>

XXX: py.test not nice: __main__.f, instead of just f

Instructions
------------

::
    >>> from metachao import aspect

default instruction::

    >>> class f(Aspect):
    ...     a = aspect.default(1)
    ...     b = aspect.default(1)
    ...     c = aspect.default(1)

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

    >>> class f(Aspect):
    ...     a = aspect.overwrite(1)
    ...     b = aspect.overwrite(1)
    ...     c = aspect.overwrite(1)

    >>> class g(Aspect):
    ...     c = aspect.overwrite(2)

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

    >>> class f(Aspect):
    ...     a = aspect.finalize(1)

    >>> class g(Aspect):
    ...     a = aspect.overwrite(2)

    >>> @f
    ... @g
    ... class C(object):
    ...     pass

    >>> C.a
    1

plumb instruction::

    >>> class f(Aspect):
    ...     @aspect.plumb
    ...     def func(_next, self):
    ...         return 2 * _next()

    >>> @f
    ... class C(object):
    ...     def func(self):
    ...         return 3

    >>> c = C()
    >>> c.func()
    6


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


Aspects on objects
~~~~~~~~~~~~~~~~~~

    >>> class emptyaspect(Aspect):
    ...     pass
    >>> d = dict(a=1, b=2)
    >>> ead = emptyaspect(d)

    >>> isinstance(ead, dict)
    True

    >>> sorted([x for x in ead])
    ['a', 'b']

    >>> ead['c'] = 3
    >>> d['c']
    3

    >>> class prefix(Aspect):
    ...     @aspect.plumb
    ...     def __iter__(_next, self):
    ...         return ('pre-' + x for x in _next())

    >>> pred = prefix(d)
    >>> sorted([x for x in pred])
    ['pre-a', 'pre-b', 'pre-c']

    >>> isinstance(pred, dict)
    True

Handle properties::

    >>> class Base(object):
    ...     def geta(self):
    ...         return self._a
    ...     def seta(self, value):
    ...         self._a = value
    ...     def dela(self):
    ...         del self._a
    ...     a = property(geta, seta, dela)

    >>> b = Base()
    >>> b.a = 1
    >>> c = Aspect(b)
    >>> c.a
    1

XXX: Do we want these::

    .. >>> c.a = 2
    .. >>> b.a
    .. 2
    .. >>> del c.a
    .. >>> b.a
    .. Traceback (most recent call last):
    ..   ...
    .. AttributeError: 'Base' object has no attribute '_a'
