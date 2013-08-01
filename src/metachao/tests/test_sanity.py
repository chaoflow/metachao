from __future__ import absolute_import

import inspect
import sys

from .compat import unittest


from .. import aspect


class Sanity(unittest.TestCase):
    def test_isclass(self):
        class A(object):
            pass

        self.assertTrue(inspect.isclass(A))
        self.assertFalse(inspect.isclass(A()))

    def test_isclass_with_erronous_getattr(self):
        class A(object):
            def __getattr__(self, name):
                """A getattr that does not raise AttributeError, ever.
                """

        self.assertTrue(inspect.isclass(A))
        # ATTENTION: inspect.isclass fails if __getattr__ is broken
        # for python <2.7
        if sys.version_info < (2, 7):
            self.assertTrue(inspect.isclass(A()))
        else:
            self.assertFalse(inspect.isclass(A()))

    def test_isclass_with_getattr(self):
        class A(object):
            def __getattr__(self, name):
                raise AttributeError

        self.assertTrue(inspect.isclass(A))
        self.assertFalse(inspect.isclass(A()))

    def test_issubclass_and_isinstance(self):
        class B(object):
            pass

        class a(aspect.Aspect):
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
