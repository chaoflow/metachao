from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class AspectABC(TestCase):
    def runTest(self):
        class base(Aspect):
            pass
        class asp1(base):
            def register(self):
                return 1
        class asp2(base):
            def register(self):
                return 2

        asp = asp1(asp2)

        class Base(object):
            pass
        class A(Base):
            pass

        Asp1 = asp1(A)
        Asp2 = asp2(A)
        AspA = asp(A)

        @asp1
        class Asp1_(A):
            pass

        @asp2
        class Asp2_(A):
            pass

        @asp
        class AspA_(A):
            pass

        self.assertEqual(Asp1().register(), 1)
        self.assertEqual(Asp2().register(), 2)
        self.assertEqual(AspA().register(), 1)
        self.assertEqual(Asp1_().register(), 1)
        self.assertEqual(Asp2_().register(), 2)
        self.assertEqual(AspA_().register(), 1)

        self.assertTrue(issubclass(asp1, base))
        self.assertTrue(issubclass(asp2, base))
        self.assertTrue(issubclass(asp, base))
        self.assertTrue(issubclass(A, Base))

        self.assertTrue(issubclass(Asp1, A))
        self.assertTrue(issubclass(Asp1_, A))
        self.assertTrue(issubclass(Asp1, Base))
        self.assertTrue(issubclass(Asp1, asp1))
        self.assertTrue(issubclass(Asp1, base))

        self.assertTrue(issubclass(Asp2, A))
        self.assertTrue(issubclass(Asp2_, A))
        self.assertTrue(issubclass(Asp2, Base))
        self.assertTrue(issubclass(Asp2, asp2))
        self.assertTrue(issubclass(Asp2, base))

        self.assertTrue(issubclass(AspA, A))
        self.assertTrue(issubclass(AspA_, A))
        self.assertTrue(issubclass(AspA, Base))
        self.assertTrue(issubclass(AspA, asp1))
        self.assertTrue(issubclass(AspA, asp2))
        self.assertTrue(issubclass(AspA, asp))
        self.assertTrue(issubclass(AspA, base))

        a1 = AspA()
        a2 = asp(A())

        self.assertTrue(isinstance(a1, AspA))
        self.assertTrue(isinstance(a1, A))
        self.assertTrue(isinstance(a1, Base))
        self.assertTrue(isinstance(a1, asp))
        self.assertTrue(isinstance(a1, asp1))
        self.assertTrue(isinstance(a1, asp2))
        self.assertTrue(isinstance(a1, base))

        # XXX: a2 is using A() as a prototype
        # What should it be an instance of?
        #self.assertTrue(isinstance(a2, A))
        #self.assertTrue(isinstance(a2, Base))
        #self.assertTrue(isinstance(a2, asp))
        #self.assertTrue(isinstance(a2, asp1))
        #self.assertTrue(isinstance(a2, asp2))
        #self.assertTrue(isinstance(a2, base))

