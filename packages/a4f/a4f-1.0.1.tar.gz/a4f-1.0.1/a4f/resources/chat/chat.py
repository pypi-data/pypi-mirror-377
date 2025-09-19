from __future__ import annotations

from ..._compat import cached_property
from ..._resource import SyncAPIResource
from .completions.completions import (
    Completions,
)

__all__ = ["Chat"]


class Chat(SyncAPIResource):
    @cached_property
    def completions(self) -> Completions:
        return Completions(self._client)