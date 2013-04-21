from __future__ import absolute_import

from .compat import unittest

from .. import aspect
from ..aspect import Aspect


class Getattr(unittest.TestCase):
    def test_origin_getattr(self):
        class A(object):
            def __getattr__(self, name):
                if name in ('a', 'b'):
                    return 1
                raise AttributeError

        class answer(Aspect):
            a = 42

        a = A()
        answering = answer(A)()
        prototyped = answer(A())

        self.assertEqual(a.a, 1)
        self.assertEqual(a.b, 1)
        self.assertEqual(answering.a, 42)
        self.assertEqual(answering.b, 1)
        self.assertEqual(prototyped.a, answering.a)
        self.assertEqual(prototyped.b, answering.b)

    def test_overwrite_getattr(self):
        class A(object):
            def __getattr__(self, name):
                if name in ('a',):
                    return 1
                raise AttributeError

        class confuse(Aspect):
            def __getattr__(self, name):
                if name in ('a',):
                    return 23
                raise AttributeError

        a = A()
        confused = confuse(A)()
        prototyped = confuse(A())

        self.assertEqual(a.a, 1)
        self.assertEqual(confused.a, 23)
        self.assertEqual(prototyped.a, confused.a)

    def test_chain_getattr(self):
        class A(object):
            def __getattr__(self, name):
                if name in ('a',):
                    return 21
                raise AttributeError

        class square(Aspect):
            @aspect.plumb
            def __getattr__(_next, self, name):
                if name in ('a',):
                    return 2 * _next(name)
                raise AttributeError

        a = A()
        squared = square(A)()
        prototyped = square(A())

        self.assertEqual(a.a, 21)
        self.assertEqual(squared.a, 42)
        self.assertEqual(prototyped.a, squared.a)
