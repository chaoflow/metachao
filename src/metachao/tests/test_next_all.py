from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class AllMethodsViaNext(TestCase):
    def runTest(self):
        class C(object):
            def f(self):
                return 1

            def g(self):
                return 2

        class a(Aspect):
            @aspect.plumb
            def g(_next, self):
                return _next() + _next.all.f()

            # @aspect.plumb
            # def h(_next, self):
            #     return _next() + _next.all.f()

        self.assertEqual(a(C()).g(), 3)
        self.assertEqual(a(C)().g(), 3)
        # self.assertEqual(a(C()).h(), 3)
        # self.assertEqual(a(C)().h(), 3)
