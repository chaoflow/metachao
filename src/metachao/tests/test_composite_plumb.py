from __future__ import absolute_import

from .compat import unittest

from metachao import aspect


def f1(_next, self):
    return "f1-" + _next()

def f2(_next, self):
    return "f2-" + _next()


class a(aspect.Aspect):
    f = aspect.composite_plumb(f1, f2)


@a
class C(object):
    def f(self):
        return "f"


class TestCompositePlumb(unittest.TestCase):
    def test(self):
        c = C()
        self.assertEqual(c.f(), "f1-f2-f")
