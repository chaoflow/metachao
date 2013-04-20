from __future__ import absolute_import

import sys


if sys.version_info[0] is 2 and sys.version_info[1] < 7:
    import unittest2 as unittest
else:
    import unittest
