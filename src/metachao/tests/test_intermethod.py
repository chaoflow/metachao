from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect


class InterMethod(unittest.TestCase):
    def runTest(self):
        class C(object):
            def f(self):
                return 1

            def g(self):
                return self.f() * 2
        c = C()

        self.assertEqual(C().f(), 1)
        self.assertEqual(C().g(), 2)

        class a1(Aspect):
            def f(self):
                return 10

        self.assertEqual(a1(C)().f(), 10)
        self.assertEqual(a1(C)().g(), 20)
        self.assertEqual(a1(c).f(), 10)

        # ATTENTION: C.f is picked instead of a1.f, because g is bound
        # to the C instance, not the new instance that uses the C
        # instance as prototype
        self.assertEqual(a1(c).g(), 2)
