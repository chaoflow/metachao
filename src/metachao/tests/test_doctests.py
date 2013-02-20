import unittest
import doctest
from pprint import pprint

optionflags = doctest.NORMALIZE_WHITESPACE | \
              doctest.ELLIPSIS | \
              doctest.REPORT_ONLY_FIRST_FAILURE

TESTFILES = [
    '../test.rst',
]

TESTMODULES = [
    'metachao._aspect',
    'metachao._instructions',
    'metachao.tools',
]

def test_suite():
    return unittest.TestSuite([
        doctest.DocTestSuite(
            module,
            optionflags=optionflags,
            ) for module in TESTMODULES
        ]+[
        doctest.DocFileSuite(
            file,
            optionflags=optionflags,
            globs={'pprint': pprint},
            ) for file in TESTFILES
        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')  #pragma NO COVERAGE
