from __future__ import absolute_import

from UserDict import UserDict

from .compat import unittest

from .. import aspect
from ..aspect import Aspect
from ..prototype import derive


class TestPrototype(unittest.TestCase):
    def setUp(self):
        class Klass(object):
            def ret_x(self):
                return self.x

            @property
            def prop_x(self):
                return self.x
            @prop_x.setter
            def prop_x(self, x):
                self.x = x
            @prop_x.deleter
            def prop_x(self):
                del self.x

        self.K = Klass
        self.a = self.K()
        self.b = derive(self.a)
        self.c = derive(self.b)

    def test_inherit_from_origin_class(self):
        self.K.x = 1
        self.assertEqual(self.a.x, 1)
        self.assertEqual(self.b.x, 1)
        self.assertEqual(self.c.x, 1)

    def test_origin_trumps_origin_class(self):
        self.K.x = 1
        self.a.x = 2
        self.assertEqual(self.a.x, 2)
        self.assertEqual(self.b.x, 2)
        self.assertEqual(self.c.x, 2)

    def test_middle_trumps_origin_class(self):
        self.K.x = 1
        self.a.x = 2
        self.b.x = 3
        self.assertEqual(self.a.x, 2)
        self.assertEqual(self.b.x, 3)
        self.assertEqual(self.c.x, 3)

    def test_final_trumps_all(self):
        self.K.x = 1
        self.a.x = 2
        self.b.x = 3
        self.c.x = 4
        self.assertEqual(self.a.x, 2)
        self.assertEqual(self.b.x, 3)
        self.assertEqual(self.c.x, 4)

    def test_delattr_reveals_next_in_chain(self):
        self.K.x = 1
        self.a.x = 2
        self.b.x = 3
        self.c.x = 4
        self.assertEqual(self.c.x, 4)
        del self.c.x
        def fail():
            del self.c.x
        self.assertRaises(AttributeError, fail)
        self.assertEqual(self.c.x, 3)
        del self.b.x
        self.assertEqual(self.c.x, 2)
        del self.a.x
        self.assertEqual(self.c.x, 1)

    def test_method_bound_to_instance_called_upon(self):
        self.K.x = 1
        self.a.x = 2
        self.b.x = 3
        self.c.x = 4
        self.assertEqual(self.a.ret_x(), 2)
        self.assertEqual(self.b.ret_x(), 3)
        self.assertEqual(self.c.ret_x(), 4)

    def test_property_bound_to_instance_called_upon(self):
        self.K.x = 1
        self.a.prop_x = 2
        self.b.prop_x = 3
        self.c.prop_x = 4
        self.assertEqual(self.a.x, 2)
        self.assertEqual(self.b.x, 3)
        self.assertEqual(self.c.x, 4)
        self.assertEqual(self.a.prop_x, 2)
        self.assertEqual(self.b.prop_x, 3)
        self.assertEqual(self.c.prop_x, 4)
        del self.c.prop_x
        self.assertEqual(self.c.x, 3)
        self.assertEqual(self.c.prop_x, 3)
        del self.b.prop_x
        self.assertEqual(self.c.x, 2)
        self.assertEqual(self.c.prop_x, 2)
        del self.a.prop_x
        self.assertEqual(self.c.x, 1)
        self.assertEqual(self.c.prop_x, 1)

    def test_explicitly_bind_method(self):
        d = derive(self.c, bind=dict(ret_x=self.c))
        e = derive(d)
        f = derive(e, bind=dict(ret_x=e))
        self.a.x = 1
        d.x = 2
        e.x = 3
        f.x = 4
        self.assertEqual(self.c.ret_x(), 1)
        self.assertEqual(d.ret_x(), 1)
        self.assertEqual(e.ret_x(), 1)
        self.assertEqual(f.ret_x(), 3)

    def test_explicitly_bind_property(self):
        d = derive(self.c, bind=dict(prop_x=self.c))
        e = derive(d)
        f = derive(e, bind=dict(prop_x=e))
        self.a.x = 1
        d.x = 2
        e.x = 3
        f.x = 4
        self.assertEqual(self.c.prop_x, 1)
        self.assertEqual(d.prop_x, 1)
        self.assertEqual(e.prop_x, 1)
        self.assertEqual(f.prop_x, 3)

    def test_dict_as_prototype(self):
        d = dict()
        e = derive(d, bind=dict(keys=d))
        d['a'] = 1
        self.assertRaises(KeyError, lambda :e['a'])
        self.assertEqual(e.keys(), d.keys())

    def test_UserDict_as_prototype(self):
        d = UserDict()
        e = derive(d)
        e = derive(d, bind=dict(keys=d))
        d['a'] = 1
        self.assertRaises(KeyError, lambda :e['a'])
        self.assertEqual(e.keys(), d.keys())

    def test_derived_isinstance_of_prototype_class(self):
        self.assertIsInstance(self.a, self.K)
        self.assertIsInstance(self.b, self.K)
        self.assertIsInstance(self.b, self.a.__class__)
        self.assertIsInstance(self.c, self.K)
        self.assertIsInstance(self.c, self.a.__class__)
        self.assertIsInstance(self.c, self.b.__class__)
