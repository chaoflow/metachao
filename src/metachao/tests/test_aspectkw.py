from __future__ import absolute_import

from .compat import unittest

from metachao import aspect
from metachao.aspect import Aspect


class Cfg(unittest.TestCase):
    def runTest(self):
        class asp(Aspect):
            _a = aspect.cfg(1)
            _b = aspect.cfg(bb=2)

        class A(object):
            pass

        # aspect with default cfg
        a = asp(A)()
        self.assertEqual(a._a, 1)
        self.assertEqual(a._b, 2)
        a = asp(A())
        self.assertEqual(a._a, 1)
        self.assertEqual(a._b, 2)

        # configured aspect
        asp1020 = asp(a=10, bb=20)
        a = asp1020(A)()
        self.assertEqual(a._a, 10)
        self.assertEqual(a._b, 20)
        a = asp1020(A())
        self.assertEqual(a._a, 10)
        self.assertEqual(a._b, 20)

        # overide configuration on aspect application
        a = asp1020(A, a=100, bb=200)()
        self.assertEqual(a._a, 100)
        self.assertEqual(a._b, 200)
        a = asp1020(A(), a=100, bb=200)
        self.assertEqual(a._a, 100)
        self.assertEqual(a._b, 200)

        # overide configuration on class init
        a = asp1020(A, a=100, bb=200)(a=1000, bb=2000)
        self.assertEqual(a._a, 1000)
        self.assertEqual(a._b, 2000)
