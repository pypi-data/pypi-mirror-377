from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Union, Mapping, Callable, Awaitable
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Timeout,
    NotGiven,
    RequestOptions,
)
from ._utils import (
    is_given,
    is_mapping,
)
from ._compat import cached_property
from ._models import FinalRequestOptions
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import A4FError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
)

if TYPE_CHECKING:
    from .resources.images import Images
    from .resources.chat.chat import Chat
    from .resources.embeddings import Embeddings
    from .resources.audio.audio import Audio

__all__ = ["Timeout", "RequestOptions", "A4F", "Client"]


class A4F(SyncAPIClient):
    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None | Callable[[], str] = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Construct a new synchronous A4F client instance.

        This automatically infers the following arguments from their corresponding environment variables if they are not provided:
        - `api_key` from `A4F_API_KEY`
        """
        if api_key is None:
            api_key = os.environ.get("A4F_API_KEY")
        if api_key is None:
            raise A4FError(
                "The api_key client option must be set either by passing api_key to the client or by setting the A4F_API_KEY environment variable"
            )
        if callable(api_key):
            self.api_key = ""
            self._api_key_provider: Callable[[], str] | None = api_key
        else:
            self.api_key = api_key
            self._api_key_provider = None

        base_url = f"https://api.a4f.co/v1"

        super().__init__(
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
        )

        self._default_stream_cls = Stream

    @cached_property
    def chat(self) -> Chat:
        from .resources.chat import Chat

        return Chat(self)

    @cached_property
    def embeddings(self) -> Embeddings:
        from .resources.embeddings import Embeddings

        return Embeddings(self)

    @cached_property
    def images(self) -> Images:
        from .resources.images import Images

        return Images(self)

    @cached_property
    def audio(self) -> Audio:
        from .resources.audio import Audio

        return Audio(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="brackets")

    def _refresh_api_key(self) -> None:
        if self._api_key_provider:
            self.api_key = self._api_key_provider()

    @override
    def _prepare_options(self, options: FinalRequestOptions) -> FinalRequestOptions:
        self._refresh_api_key()
        return super()._prepare_options(options)

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        if not api_key:
            # if the api key is an empty string, encoding the header will fail
            return {}
        return {"Authorization": f"Bearer {api_key}"}

    def copy(
        self,
        *,
        api_key: str | Callable[[], str] | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        max_retries: int | NotGiven = NOT_GIVEN,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self._api_key_provider or self.api_key,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        data = body.get("error", body) if is_mapping(body) else body
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=data)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=data)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=data)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=data)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=data)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=data)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=data)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=data)
        return APIStatusError(err_msg, response=response, body=data)