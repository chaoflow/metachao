from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class Sanity(TestCase):
    def runTest(self):
        self.issubclass_and_isinstance()

    def issubclass_and_isinstance(self):
        class B(object):
            pass

        class a(Aspect):
            pass

        C1 = a(B)
        c1 = C1()

        @a
        class C2(B):
            pass
        c2 = C2()

        self.assertTrue(issubclass(C1, B))
        self.assertTrue(isinstance(c1, B))
        self.assertTrue(isinstance(c1, C1))
        self.assertTrue(issubclass(C2, B))
        self.assertTrue(isinstance(c2, B))
        self.assertTrue(isinstance(c2, C2))
