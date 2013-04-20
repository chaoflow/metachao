from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect


class AspectInheritance(unittest.TestCase):
    def runTest(self):
        class base(Aspect):
            a = 0
            b = 0
        class asp1(base):
            a = 1
        class asp2(base):
            a = 2

        class A(object):
            __metachao_effective__ = {}

        a1 = asp1(A)()
        b = base(A)()
        a2 = asp2(A)()

        self.assertEqual(b.a, 0)
        self.assertEqual(b.b, 0)
        self.assertEqual(a1.a, 1)
        self.assertEqual(a1.b, 0)
        self.assertEqual(a2.a, 2)
        self.assertEqual(a2.b, 0)
