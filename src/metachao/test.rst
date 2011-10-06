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

Handle properties, changes only take effect on the new object, the
other is used as prototype::

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

    >>> c.a = 2
    >>> c.a
    2
    >>> b.a
    1
    >>> del c.a
    >>> c.a
    1
    >>> del c.a
    Traceback (most recent call last):
      ...
    AttributeError: _a

XXX: not sure whether this is really what we want. Does applying an
empty aspect mean, that we get an object using the one passed to
aspect as prototype for attribute access? I think yes, because
e.g. for a prefix aspect that adds a prefix to dictionary keys, we
need a place to store the prefix: the instance.

Applying property twice works two, but is not really needed::

    >>> class Base(object):
    ...     pass

    >>> class prop(Aspect):
    ...     def geta(self):
    ...         return self._a
    ...     def seta(self, value):
    ...         self._a = value
    ...     a = property(geta, seta)

    >>> b = Base()
    >>> p = prop(b)
    >>> p.a = 1
    >>> p.a
    1
    >>> '_a' in dir(b)
    False
    >>> '_a' in dir(p)
    True

    >>> pp = prop(p)
    >>> pp.a
    1
    >>> '_a' in dir(pp)
    False
    >>> pp._a
    1
    >>> pp.a = 2
    >>> pp.a
    2
    >>> p.a
    1


__dict__ keys of a plain class are as expected::

    >>> class Plain(object):
    ...     pass
    >>> sorted(Plain.__dict__.keys())
    ['__dict__', '__doc__', '__module__', '__weakref__']
    >>> from metachao._aspect import DICT_KEYS_OF_PLAIN_CLASS
    >>> DICT_KEYS_OF_PLAIN_CLASS == sorted(Plain.__dict__.keys())
    True

Edge case::

    >>> class aspect1(Aspect):
    ...     a = 1
    >>> class aspect2(Aspect):
    ...     b = 2
    >>> @aspect1
    ... class Foo(object):
    ...     c = 3

    >>> foo = aspect2(Foo())
    >>> foo = aspect2(Foo)()
