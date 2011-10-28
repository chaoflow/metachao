from unittest import TestCase

from metachao import aspect
from metachao.aspect import Aspect


class ModuleAndName(TestCase):
    def runTest(self):
        class A(object):
            pass
        self.assertEqual(A.__module__, 'metachao.tests.test_moduleandname')
        self.assertEqual(A.__name__, 'A')

        class a(Aspect):
            pass
        @a
        class A(Aspect):
            pass
        self.assertEqual(A.__module__, 'metachao.tests.test_moduleandname')
        self.assertEqual(A.__name__, 'A')
