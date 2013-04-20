from __future__ import absolute_import

from .compat import unittest

from metachao import aspect
from metachao.aspect import Aspect


class DefaultWith__name__(unittest.TestCase):
    def runTest(self):
        class C(object):
            pass
        c = C()

        class a(Aspect):
            __name__ = aspect.default('bob')

        self.assertEqual(a(C)().__name__, 'bob')
        self.assertEqual(a(c).__name__, 'bob')
