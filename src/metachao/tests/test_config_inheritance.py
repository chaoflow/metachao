from __future__ import absolute_import

from .compat import unittest

from metachao import aspect


class base(aspect.Aspect):
    base = aspect.config('base')
    child = aspect.config('base')


class child(base):
    child = aspect.config('child')


class C(object):
    pass


class TestConfigInheritance(unittest.TestCase):
    def test_default_values(self):
        self.assertEqual(child(C)().base, 'base')
        self.assertEqual(child(C)().child, 'child')
        self.assertEqual(child(C()).base, 'base')
        self.assertEqual(child(C()).child, 'child')

    def test_preconfigure(self):
        global child
        child = child(base='preconfigured', child='preconfigured')
        self.assertEqual(child(C)().base, 'preconfigured')
        self.assertEqual(child(C)().child, 'preconfigured')
        self.assertEqual(child(C()).base, 'preconfigured')
        self.assertEqual(child(C()).child, 'preconfigured')
