from __future__ import annotations

import os as _os
from typing_extensions import override

from . import types
from ._types import NOT_GIVEN, NoneType, NotGiven
from ._client import A4F, Stream, Timeout, RequestOptions
from ._models import BaseModel
from ._response import APIResponse as APIResponse, AsyncAPIResponse as AsyncAPIResponse
from ._constants import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES, DEFAULT_CONNECTION_LIMITS
from ._exceptions import (
    APIError,
    A4FError,
    ConflictError,
    NotFoundError,
    APIStatusError,
    RateLimitError,
    APITimeoutError,
    BadRequestError,
    APIConnectionError,
    AuthenticationError,
    InternalServerError,
    PermissionDeniedError,
    LengthFinishReasonError,
    UnprocessableEntityError,
    APIResponseValidationError,
    InvalidWebhookSignatureError,
    ContentFilterFinishReasonError,
)
from ._utils._logs import setup_logging as _setup_logging
from ._legacy_response import HttpxBinaryResponseContent as HttpxBinaryResponseContent

__all__ = [
    "types",
    "__title__",
    "NoneType",
    "Transport",
    "NotGiven",
    "NOT_GIVEN",
    "Omit",
    "A4FError",
    "APIError",
    "APIStatusError",
    "APITimeoutError",
    "APIConnectionError",
    "APIResponseValidationError",
    "BadRequestError",
    "AuthenticationError",
    "PermissionDeniedError",
    "NotFoundError",
    "ConflictError",
    "UnprocessableEntityError",
    "RateLimitError",
    "InternalServerError",
    "LengthFinishReasonError",
    "ContentFilterFinishReasonError",
    "InvalidWebhookSignatureError",
    "Timeout",
    "RequestOptions",
    "Client",
    "Stream",
    "A4F",
    "BaseModel",
    "DEFAULT_TIMEOUT",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_CONNECTION_LIMITS",
]

_setup_logging()

# ------ Module level client ------
import typing as _t
import typing_extensions as _te

import httpx as _httpx

from ._base_client import DEFAULT_TIMEOUT, DEFAULT_MAX_RETRIES

api_key: str | None = None

timeout: float | Timeout | None = DEFAULT_TIMEOUT

max_retries: int = DEFAULT_MAX_RETRIES

class _ModuleClient(A4F):
    # Note: we have to use type: ignores here as overriding class members
    # with properties is technically unsafe but it is fine for our use case

    @property  # type: ignore
    @override
    def api_key(self) -> str | None:
        return api_key

    @api_key.setter  # type: ignore
    def api_key(self, value: str | None) -> None:  # type: ignore
        global api_key

        api_key = value

    @property  # type: ignore
    @override
    def timeout(self) -> float | Timeout | None:
        return timeout

    @timeout.setter  # type: ignore
    def timeout(self, value: float | Timeout | None) -> None:  # type: ignore
        global timeout

        timeout = value

    @property  # type: ignore
    @override
    def max_retries(self) -> int:
        return max_retries

    @max_retries.setter  # type: ignore
    def max_retries(self, value: int) -> None:  # type: ignore
        global max_retries

        max_retries = value

def _has_a4f_credentials() -> bool:
    return _os.environ.get("A4F_API_KEY") is not None

_client: A4F | None = None


def _load_client() -> A4F:  # type: ignore[reportUnusedFunction]
    global _client

    if _client is None:

        _client = _ModuleClient(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        return _client

    return _client


def _reset_client() -> None:  # type: ignore[reportUnusedFunction]
    global _client

    _client = None


from ._module_client import (
    chat as chat,
    audio as audio,
    images as images,
    embeddings as embeddings,
)
