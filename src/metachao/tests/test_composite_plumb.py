from __future__ import absolute_import

from .compat import unittest

from metachao import aspect


def f1(_next, self):
    return "f1-" + _next()

def f2(_next, self):
    return "f2-" + _next()


class a(aspect.Aspect):
    f = aspect.composite_plumb([f1, f2])


@a
class C(object):
    def f(self):
        return "f"


class D(object):
    def f(self):
        return "g"


class TestCompositePlumb(unittest.TestCase):
    def test_composite_plumb_class(self):
        c = C()
        self.assertEqual(c.f(), "f1-f2-f")

    def test_composite_plumb_instance(self):
        self.assertEqual(a(D()).f(), "f1-f2-g")
