from __future__ import annotations

from typing_extensions import Literal
import httpx

from .... import _legacy_response
from ...._types import NOT_GIVEN, Body, Query, NotGiven
from ...._utils import maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource
from ...._response import to_streamed_response_wrapper
from ....pagination import SyncCursorPage
from ...._base_client import make_request_options
from ....types.chat.completions import message_list_params
from ....types.chat.chat_completion_store_message import ChatCompletionStoreMessage

__all__ = ["Messages"]


class Messages(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MessagesWithRawResponse:
        """
        Return raw response objects instead of parsed content.
        """
        return MessagesWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MessagesWithStreamingResponse:
        """
        Return streamed responses without eagerly reading the body.
        """
        return MessagesWithStreamingResponse(self)

    def list(
        self,
        completion_id: str,
        *,
        after: str | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        order: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[ChatCompletionStoreMessage]:
        """Get the messages in a stored chat completion."""
        if not completion_id:
            raise ValueError(f"Expected a non-empty value for `completion_id` but received {completion_id!r}")
        return self._get_api_list(
            f"/chat/completions/{completion_id}/messages",
            page=SyncCursorPage[ChatCompletionStoreMessage],
            options=make_request_options(
                query=maybe_transform(
                    {
                        "after": after,
                        "limit": limit,
                        "order": order,
                    },
                    message_list_params.MessageListParams,
                ),
            ),
            model=ChatCompletionStoreMessage,
        )


class MessagesWithRawResponse:
    def __init__(self, messages: Messages) -> None:
        self._messages = messages
        self.list = _legacy_response.to_raw_response_wrapper(messages.list)


class MessagesWithStreamingResponse:
    def __init__(self, messages: Messages) -> None:
        self._messages = messages
        self.list = to_streamed_response_wrapper(messages.list)