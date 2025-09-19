from __future__ import annotations

from .speech import (
    Speech,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource
from .transcriptions import (
    Transcriptions,
)

__all__ = ["Audio"]


class Audio(SyncAPIResource):
    @cached_property
    def transcriptions(self) -> Transcriptions:
        return Transcriptions(self._client)

    @cached_property
    def speech(self) -> Speech:
        return Speech(self._client)