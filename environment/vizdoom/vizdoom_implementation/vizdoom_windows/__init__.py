import sys as _sys

_COMPILED_PYTHON_VERSION = "3.7.4"

_this_python_version = "{}.{}.{}".format(*_sys.version_info[0:3])

if _COMPILED_PYTHON_VERSION != _this_python_version:
    raise SystemError(
        "This interpreter version: '{}' doesn't match with version of the interpreter ViZDoom was compiled with: {}".format(
            _this_python_version, _COMPILED_PYTHON_VERSION))

from .vizdoom import __version__ as __version__
from .vizdoom import *

import os as _os

scenarios_path = _os.path.join(__path__[0], "../vizdoomgym/scenarios")
wads = [wad for wad in sorted(_os.listdir(scenarios_path)) if wad.endswith(".wad")]
configs = [cfg for cfg in sorted(_os.listdir(scenarios_path)) if cfg.endswith(".cfg")]
