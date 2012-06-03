from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class AspectABC(TestCase):
    def runTest(self):
        class base(Aspect):
            pass
        class asp1(base):
            pass
        class asp2(base):
            pass

        @asp1
        class A1(object):
            pass

        @asp2
        class A2(object):
            pass

        self.assertTrue(issubclass(asp1, base))
        self.assertTrue(issubclass(asp2, base))
        self.assertTrue(issubclass(A1, base))
        self.assertTrue(issubclass(A2, base))
        self.assertTrue(issubclass(A1, asp1))
        self.assertTrue(issubclass(A2, asp2))
