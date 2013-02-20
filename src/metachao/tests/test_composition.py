from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class Compositions(TestCase):
    def runTest(self):
        class a1(Aspect):
            a = 1
            b = aspect.default(1)
            c = aspect.default(1)
            d = aspect.default(1)
            e = aspect.default(1)
        class a2(Aspect):
            a = 2
            b = 2
            c = aspect.default(2)
            d = aspect.default(2)
        class a3(Aspect):
            a = 3
            b = 3
            c = 3

        a123 = a1(a2(a3))
        a12 = a1(a2)
        a12_3 = a12(a3)
        a23 = a2(a3)
        a1_23 = a1(a23)

        class C(object):
            pass
