from unittest import TestCase

from metachao._instructions import Instruction


class InstrRepr(TestCase):
    def runTest(self):
        i = Instruction(None, name='NAME')
        self.assertEqual(i.name, 'NAME')
        self.assertEqual(repr(i), "<Instruction 'NAME' None>")
