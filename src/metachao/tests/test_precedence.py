from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect


class Precedence(unittest.TestCase):
    def runTest(self):
        self.default()
        self.undecorated()
        # for now we try how it feels if undecorated attributes just
        # overwrite like with inheritance - so far it feels more pythonic
        #self.overwrite()
        #self.finalize()

    def default(self):
        class B(object):
            a = 1

        class a(Aspect):
            a = aspect.default(10)
            b = aspect.default(20)

        C1 = a(B)

        @a
        class C2(B):
            a = 2

        c1 = C1()
        c2 = C2()
        ab = a(B())

        self.assertEqual(C1.a, 1)
        self.assertEqual(C1.b, 20)
        self.assertEqual(C2.a, 2)
        self.assertEqual(C2.b, 20)
        self.assertEqual(c1.a, 1)
        self.assertEqual(c1.b, 20)
        self.assertEqual(c2.a, 2)
        self.assertEqual(c2.b, 20)
        self.assertEqual(ab.a, 1)
        self.assertEqual(ab.b, 20)

    def undecorated(self):
        class B(object):
            a = 1

        class a(Aspect):
            a = 10

        C1 = a(B)

        @a
        class C2(B):
            a = 2

        c1 = C1()
        c2 = C2()
        ab = a(B())

        self.assertEqual(C1.a, 10)
        self.assertEqual(C2.a, 10)
        self.assertEqual(c1.a, 10)
        self.assertEqual(c2.a, 10)
        self.assertEqual(ab.a, 10)
