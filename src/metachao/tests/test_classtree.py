from __future__ import absolute_import

from .compat import unittest

from metachao import classtree
from metachao.classtree import OrderedDict


class TestClassnode(unittest.TestCase):
    def setUp(self):
        class Base(classtree.Base):
            pass

        class A(Base):
            pass

        class B(Base):
            pass

        self.Base = Base
        self.A = A
        self.B = B

    def test_setgetitem(self):
        self.Base['a'] = self.A
        self.Base['b'] = self.B
        self.assertEqual(self.Base['a'], self.A)
        self.assertEqual(self.Base['b'], self.B)

    def test_keys(self):
        self.Base['a'] = self.A
        self.Base['b'] = self.B
        self.assertEqual(self.Base.keys(), ['a', 'b'])

    def test_keeps_order(self):
        self.Base['b'] = self.B
        self.Base['a'] = self.A
        self.assertEqual(self.Base.keys(), ['b', 'a'])

    def test_each_class_has_own_child_storage(self):
        self.Base['a'] = self.A
        self.Base['b'] = self.B
        self.assertEqual(self.Base.keys(), ['a', 'b'])
        self.assertEqual(self.A.keys(), [])
        self.assertEqual(self.B.keys(), [])

        self.A['b'] = self.B
        self.B['a'] = self.A
        self.assertEqual(self.Base.keys(), ['a', 'b'])
        self.assertEqual(self.A.keys(), ['b'])
        self.assertEqual(self.B.keys(), ['a'])


class TestInstantiation(unittest.TestCase):
    def setUp(self):
        class Base(classtree.Node):
            pass

        class Root(Base):
            pass

        class A(Base):
            pass

        class AA(Base):
            pass

        class AB(Base):
            pass

        class B(Base):
            pass

        Root['a'] = A
        Root['a']['a'] = AA
        Root['a']['b'] = AB
        Root['b'] = B

        self.Root = Root
        self.A = A
        self.AA = AA
        self.AB = AB
        self.B = B

    def test_instantiation(self):
        root = self.Root()
        self.assertTrue(isinstance(root, self.Root))
        self.assertTrue(isinstance(root['a'], self.A))
        self.assertTrue(isinstance(root['a']['a'], self.AA))
        self.assertTrue(isinstance(root['a']['b'], self.AB))
        self.assertTrue(isinstance(root['b'], self.B))

        self.assertIs(root['a'], root['a'])
        self.assertIs(root['a']['a'], root['a']['a'])
        self.assertIs(root['a']['b'], root['a']['b'])
        self.assertIs(root['b'], root['b'])
