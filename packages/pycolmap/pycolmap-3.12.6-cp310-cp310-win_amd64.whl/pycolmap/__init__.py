"""""" # start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pycolmap.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import textwrap
from typing import TYPE_CHECKING

from .utils import import_module_symbols

try:
    from . import _core
except ImportError as e:
    raise RuntimeError(
        textwrap.dedent("""
        Cannot import the C++ backend pycolmap._core.
        Make sure that you successfully install the package with
          $ python -m pip install pycolmap/
        """)
    ) from e

# Type checkers cannot deal with dynamic manipulation of globals.
# Instead, we use the same workaround as PyTorch.
if TYPE_CHECKING:
    from ._core import *  # noqa F403

__all__ = import_module_symbols(globals(), _core, exclude={"cost_functions"})
__all__.extend(["__version__", "__ceres_version__"])

__version__ = _core.__version__
__ceres_version__ = _core.__ceres_version__
