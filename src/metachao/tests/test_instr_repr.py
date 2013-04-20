from __future__ import absolute_import

from .compat import unittest

from .._instructions import Instruction


class InstrRepr(unittest.TestCase):
    def runTest(self):
        i = Instruction(None, name='NAME')
        self.assertEqual(i.name, 'NAME')
        self.assertEqual(repr(i), "<Instruction 'NAME' None>")
