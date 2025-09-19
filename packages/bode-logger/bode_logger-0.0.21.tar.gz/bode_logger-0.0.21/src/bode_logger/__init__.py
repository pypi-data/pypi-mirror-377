from importlib.metadata import version as _get_version_str
from ._bode_logger import _update_root_logger
from ._bode_logger import info, debug, warning, error, critical, get_logger

__version__ = _get_version_str("bode_logger")
_update_root_logger()
