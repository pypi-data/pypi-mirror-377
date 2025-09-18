# flake8: noqa

import importlib.util

from ._base import *
from ._sync import *

_async_package_name = "aiohttp"
_async_spec = importlib.util.find_spec(_async_package_name)

if _async_spec is not None:
    from ._async import *
