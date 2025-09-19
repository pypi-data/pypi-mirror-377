from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `a4f.resources` module.

    This is used so that we can lazily import `a4f.resources` only when
    needed *and* so that users can just import `a4f` and reference `a4f.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("a4f.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
