from __future__ import annotations

from typing_extensions import Literal, TypedDict


__all__ = ["CompletionListParams"]


class CompletionListParams(TypedDict, total=False):
    after: str
    """Identifier for the last chat completion from the previous pagination request."""

    limit: int
    """Number of Chat Completions to retrieve."""

    model: str
    """The model used to generate the Chat Completions."""

    order: Literal["asc", "desc"]
    """Sort order for Chat Completions by timestamp.

    Use `asc` for ascending order or `desc` for descending order. Defaults to `asc`.
    """