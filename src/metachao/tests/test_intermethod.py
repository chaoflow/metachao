from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class InterMethod(TestCase):
    def runTest(self):
        self.test1()

    def test1(self):
        class C(object):
            def f(self):
                return 1

            def g(self):
                return self.f() * 2

        self.assertEqual(C().f(), 1)
        self.assertEqual(C().g(), 2)

        class a1(Aspect):
            def f(self):
                return 10

        #self.assertEqual(a1(C)().f(), 10)
        #self.assertEqual(a1(C)().g(), 20)
        #self.assertEqual(a1(C()).f(), 10)
        #self.assertEqual(a1(C()).g(), 20)
