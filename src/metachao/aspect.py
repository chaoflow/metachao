from __future__ import absolute_import

from . import _aspect
from . import _compose
from . import _instructions

Aspect = _aspect.Aspect

child = _instructions.child
config = _instructions.config
default = _instructions.default
plumb = _instructions.plumb

compose = _compose.compose

# legacy?
cfg = _instructions.cfg
aspectkw = _instructions.aspectkw
