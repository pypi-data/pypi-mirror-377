from __future__ import annotations

from typing import TYPE_CHECKING, Iterator, TypeVar
from functools import partial

from ..._streaming import Stream
from .chat_completion_chunk import ChatCompletionChunk

if TYPE_CHECKING:
    from .chat_completion_tool_union_param import ChatCompletionToolUnionParam

T = TypeVar("T")


class ChatCompletionStreamManager:
    def __init__(
        self,
        api_request: partial[Stream[ChatCompletionChunk]],
        input_tools: Iterator[ChatCompletionToolUnionParam] | None = None,
    ) -> None:
        self._api_request = api_request
        self._input_tools = input_tools
        self._stream: Stream[ChatCompletionChunk] | None = None

    def __enter__(self) -> "ChatCompletionStreamManager":
        self._stream = self._api_request()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._stream:
            self._stream.close()

    def __iter__(self) -> Iterator[ChatCompletionChunk]:
        if not self._stream:
            raise RuntimeError("Stream not initialized. Use with statement to initialize.")
        return iter(self._stream)