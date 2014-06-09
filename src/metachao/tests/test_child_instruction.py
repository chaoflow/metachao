from __future__ import absolute_import

from .compat import unittest

from metachao import aspect


class children_ab(aspect.Aspect):
    @aspect.child(key='@a')
    def a(self, key):
        try:
            return self._a
        except AttributeError:
            raise KeyError('a')

    @a.setter
    def a(self, key, value):
        self._a = value

    @a.deleter
    def a(self, key):
        del self._a

    def _getitem_b(self, key):
        try:
            return self._b
        except AttributeError:
            raise KeyError('b')

    def _setitem_b(self, key, value):
        self._b = value

    def _delitem_b(self, key):
        del self._b

    b = aspect.child(_getitem_b, _setitem_b, _delitem_b)

    getonly = aspect.child(lambda self, key: None)
    setonly = aspect.child(None, lambda self, key, value: None)
    delonly = aspect.child(None, None, lambda self, key: None)


@children_ab
class C(dict):
    pass


def getit(c):
    return c['getonly']


def setit(c):
    c['getonly'] = 1


def delit(c):
    del c['delonly']


class TestChild(unittest.TestCase):
    def test_getitem(self):
        c = C(x=10)
        c._a = 1
        c._b = 2
        self.assertEqual(c['@a'], 1)
        self.assertEqual(c['b'], 2)
        self.assertEqual(c['x'], 10)

    def test_setitem(self):
        c = C()
        c['@a'] = 1
        c['b'] = 2
        c['x'] = 10
        self.assertEqual(c._a, 1)
        self.assertEqual(c._b, 2)
        self.assertEqual(dict.__getitem__(c, 'x'), 10)

    def test_delitem(self):
        c = C(x=10)
        c._a = 1
        c._b = 2
        self.assertEqual(c['@a'], 1)
        self.assertEqual(c['b'], 2)
        del c['@a']
        del c['b']
        del c['x']
        self.assertFalse(hasattr(c, '@a'))
        self.assertFalse(hasattr(c, 'b'))
        self.assertFalse(dict.__contains__(c, 'x'))

    def test_getonly(self):
        c = C()
        self.assertIsNone(getit(c))
        self.assertRaises(KeyError, setit(c))
        self.assertRaises(KeyError, delit(c))

    def test_setonly(self):
        c = C()
        self.assertRaises(KeyError, getit(c))
        self.assertIsNone(setit(c))
        self.assertRaises(KeyError, delit(c))

    def test_delonly(self):
        c = C()
        self.assertRaises(KeyError, getit(c))
        self.assertRaises(KeyError, setit(c))
        self.assertIsNone(delit(c))
