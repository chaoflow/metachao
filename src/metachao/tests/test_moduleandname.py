from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect


class ModuleAndName(unittest.TestCase):
    def runTest(self):
        class A(object):
            pass
        self.assertEqual(A.__module__, 'metachao.tests.test_moduleandname')
        self.assertEqual(A.__name__, 'A')

        # XXX: in case of a composition a new Aspect class is created
        # in metachao._aspect. Therefore the module name is wrong
        #
        # Not sure whether it's worth fixing that
        #
        # class a(Aspect):
        #     pass
        # @a
        # class A(Aspect):
        #     pass
        # self.assertEqual(A.__module__, 'metachao.tests.test_moduleandname')
        # self.assertEqual(A.__name__, 'A')
