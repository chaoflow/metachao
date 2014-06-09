from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect

# XXX: rework to be more structured

class a1(Aspect):
    a = 1
    b = 1

    @aspect.plumb
    def f(_next, self):
        return 'a1,' + _next()


@a1
class a2(Aspect):
    b = 2
    c = 2
    @aspect.plumb
    def f(_next, self):
        return 'a2,' + _next()


class a3(a2):
    a = 3
    c = 3
    @aspect.plumb
    def f(_next, self):
        return 'a3,' + _next()


class A(object):
    def f(self):
        return 'A'


class MultiAspect(unittest.TestCase):
    def test1(self):
        x = a1(A)()
        y = a1(A())

        self.assertEqual(x.a, 1)
        self.assertEqual(x.b, 1)
        self.assertEqual(x.f(), 'a1,A')
        self.assertEqual(y.a, x.a)
        self.assertEqual(y.b, x.b)
        self.assertEqual(y.f(), x.f())

        x = a1(a1(A))()
        y = a1(a1(A)())
        z = a1(a1(A()))
        u = a1(a1)(A)()
        v = a1(a1)(A())

        self.assertEqual(x.a, 1)
        self.assertEqual(x.b, 1)
        self.assertEqual(x.f(), 'a1,a1,A')
        self.assertEqual(y.a, x.a)
        self.assertEqual(y.b, x.b)
        self.assertEqual(y.f(), x.f())
        self.assertEqual(z.a, x.a)
        self.assertEqual(z.b, x.b)
        self.assertEqual(z.f(), x.f())
        self.assertEqual(u.a, x.a)
        self.assertEqual(u.b, x.b)
        self.assertEqual(u.f(), x.f())
        self.assertEqual(v.a, x.a)
        self.assertEqual(v.b, x.b)
        self.assertEqual(v.f(), x.f())


    def test2(self):
        x = a2(A)()
        y = a2(A())

        self.assertEqual(x.a, 1)
        self.assertEqual(x.b, 1)
        self.assertEqual(x.c, 2)
        self.assertEqual(x.f(), 'a1,a2,A')
        self.assertEqual(y.a, x.a)
        self.assertEqual(y.b, x.b)
        self.assertEqual(y.c, x.c)
        self.assertEqual(y.f(), x.f())

    def test3(self):
        x = a3(A)()
        y = a3(A())

        self.assertEqual(x.a, 3)
        self.assertEqual(x.b, 1)
        self.assertEqual(x.c, 3)
        self.assertEqual(x.f(), 'a3,A')
        self.assertEqual(y.a, x.a)
        self.assertEqual(y.b, x.b)
        self.assertEqual(y.c, x.c)
        self.assertEqual(y.f(), x.f())
