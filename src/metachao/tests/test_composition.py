from __future__ import absolute_import

from .compat import unittest

from metachao import aspect


class default1(aspect.Aspect):
    @aspect.default
    def f(self):
        return "default1"


class default2(aspect.Aspect):
    @aspect.default
    def f(self):
        return "default2"


class overwrite1(aspect.Aspect):
    def f(self):
        return "overwrite1"


class overwrite2(aspect.Aspect):
    def f(self):
        return "overwrite2"


class plumb(aspect.Aspect):
    @aspect.plumb
    def f(_next, self):
        return "plumb-" + _next()


class config1(aspect.Aspect):
    config1 = aspect.config(config1='default')


class config2(aspect.Aspect):
    config2 = aspect.config(config2='default')


class config3(aspect.Aspect):
    config3 = aspect.config(config3='default')


class base(aspect.Aspect):
    base = 'base'
    child = 'base'


class child1(base):
    child = 'child1'


class child2(base):
    child = 'child2'


class C(object):
    def f(self):
        return "C"


class D(object):
    pass


class TestCompositions(unittest.TestCase):
    """Aspects can first be composed, then be applied

    TODO: composition with config in all permutations
    TODO: show compose(a,b,c) == a(b(c)) == a(b)(c)
    """
    def test_overwrite_overwrite_plumb_plumb(self):
        composition = aspect.compose(
            plumb,
            plumb,
            overwrite2,
            overwrite1,
        )
        self.assertEqual(composition(C)().f(), "plumb-plumb-overwrite2")
        self.assertEqual(composition(C()).f(), "plumb-plumb-overwrite2")
        self.assertEqual(composition(D)().f(), "plumb-plumb-overwrite2")
        self.assertEqual(composition(D()).f(), "plumb-plumb-overwrite2")

    def test_default_default_plumb_plumb(self):
        composition = aspect.compose(
            plumb,
            plumb,
            default2,
            default1,
        )
        self.assertEqual(composition(C)().f(), "plumb-plumb-C")
        self.assertEqual(composition(C()).f(), "plumb-plumb-C")
        self.assertEqual(composition(D)().f(), "plumb-plumb-default1")
        self.assertEqual(composition(D()).f(), "plumb-plumb-default1")

    def test_default_overwrite_plumb_plumb(self):
        composition = aspect.compose(
            plumb,
            plumb,
            overwrite1,
            default1,
        )
        self.assertEqual(composition(C)().f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(C()).f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(D)().f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(D()).f(), "plumb-plumb-overwrite1")

    def test_overwrite_default_plumb_plumb(self):
        composition = aspect.compose(
            plumb,
            plumb,
            default1,
            overwrite1,
        )
        self.assertEqual(composition(C)().f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(C()).f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(D)().f(), "plumb-plumb-overwrite1")
        self.assertEqual(composition(D()).f(), "plumb-plumb-overwrite1")

    def test_configuration(self):
        composition = aspect.compose(
            config1,
            config2(config2='preconfigured'),
            config3(config3='preconfigured'),
        )
        composition = composition(
            config3='composition',
        )
        self.assertEqual(composition(C)().config1, 'default')
        self.assertEqual(composition(C()).config1, 'default')
        self.assertEqual(composition(C)().config2, 'preconfigured')
        self.assertEqual(composition(C()).config2, 'preconfigured')
        self.assertEqual(composition(C)().config3, 'composition')
        self.assertEqual(composition(C()).config3, 'composition')
        self.assertEqual(
            composition(C, config3='application')().config3,
            'application'
        )
        self.assertEqual(
            composition(C(), config3='application').config3,
            'application'
        )
        self.assertEqual(
            composition(C, config3='application')(
                config3='instantiation'
            ).config3,
            'instantiation'
        )

    def test_inheritance(self):
        composition = aspect.compose(
            child1,
            child2,
        )
        self.assertEqual(composition(C)().base, 'base')
        self.assertEqual(composition(C)().child, 'child1')
        self.assertEqual(composition(C()).base, 'base')
        self.assertEqual(composition(C()).child, 'child1')
