from __future__ import absolute_import

from .compat import unittest
from ..aspect import Aspect
from .. import utils


class TestUtils(unittest.TestCase):
    def test_isclass_oldstyle(self):
        class Old:
            pass

        o = Old()

        self.assertTrue(utils.isclass(Old))
        self.assertFalse(utils.isclass(o))

    def test_isclass_newstyle(self):
        class New(object):
            pass

        n = New()

        self.assertTrue(utils.isclass(New))
        self.assertFalse(utils.isclass(n))

    def test_isclass_meta(self):
        class meta(type):
            pass

        self.assertTrue(utils.isclass(meta))

    def test_isclass_aspect(self):
        self.assertTrue(utils.isclass(Aspect))
