from __future__ import absolute_import

from .compat import unittest

from metachao.classnode import classnode
from metachao.classnode import ClassNode
from metachao.classnode import OrderedDict


class TestClassnode(unittest.TestCase):
    def setUp(self):
        class Base(ClassNode):
            pass

        class A(Base):
            pass

        class B(Base):
            pass

        class Node(OrderedDict):
            __metaclass__ = classnode

        self.Base = Base
        self.A = A
        self.B = B
        self.Node = Node

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
