from __future__ import annotations

import array
import base64
from typing import Union, Iterable, cast
from typing_extensions import Literal


from ..types import embedding_create_params
from .._types import NOT_GIVEN, NotGiven, SequenceNotStr
from .._utils import is_given, maybe_transform
from .._extras import numpy as np, has_numpy
from .._resource import SyncAPIResource
from .._base_client import make_request_options
from ..types.create_embedding_response import CreateEmbeddingResponse

__all__ = ["Embeddings"]


class Embeddings(SyncAPIResource):

    def create(
        self,
        *,
        input: Union[str, SequenceNotStr[str], Iterable[int], Iterable[Iterable[int]]],
        model: Union[str],
        dimensions: int | NotGiven = NOT_GIVEN,
        encoding_format: Literal["float", "base64"] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
    ) -> CreateEmbeddingResponse:
        """
        Creates an embedding vector representing the input text.

        Args:
          input: Input text to embed, encoded as a string or array of tokens. To embed multiple
              inputs in a single request, pass an array of strings or array of token arrays.
              The input must not exceed the max input tokens for the model (8192 tokens for
              all embedding models), cannot be an empty string, and any array must be 2048
              dimensions or less.
              [Example Python code](https://cookbook.a4f.com/examples/how_to_count_tokens_with_tiktoken)
              for counting tokens. In addition to the per-input token limit, all embedding
              models enforce a maximum of 300,000 tokens summed across all inputs in a single
              request.

          model: ID of the model to use. You can use the
              [List models](https://platform.a4f.com/docs/api-reference/models/list) API to
              see all of your available models, or see our
              [Model overview](https://platform.a4f.com/docs/models) for descriptions of
              them.

          dimensions: The number of dimensions the resulting output embeddings should have. Only
              supported in `text-embedding-3` and later models.

          encoding_format: The format to return the embeddings in. Can be either `float` or
              [`base64`](https://pypi.org/project/pybase64/).

          user: A unique identifier representing your end-user, which can help A4F to monitor
              and detect abuse.
              [Learn more](https://platform.a4f.com/docs/guides/safety-best-practices#end-user-ids).

        """
        params = {
            "input": input,
            "model": model,
            "user": user,
            "dimensions": dimensions,
            "encoding_format": encoding_format,
        }
        if not is_given(encoding_format):
            params["encoding_format"] = "float"

        def parser(obj: CreateEmbeddingResponse) -> CreateEmbeddingResponse:
            if is_given(encoding_format):
                # don't modify the response object if a user explicitly asked for a format
                return obj

            if not obj.data:
                raise ValueError("No embedding data received")

            for embedding in obj.data:
                data = cast(object, embedding.embedding)
                if not isinstance(data, str):
                    continue
                if not has_numpy():
                    # use array for base64 optimisation
                    embedding.embedding = array.array("f", base64.b64decode(data)).tolist()
                else:
                    embedding.embedding = np.frombuffer(  # type: ignore[no-untyped-call]
                        base64.b64decode(data), dtype="float32"
                    ).tolist()

            return obj

        return self._post(
            "/embeddings",
            body=maybe_transform(params, embedding_create_params.EmbeddingCreateParams),
            options=make_request_options(
                post_parser=parser,
            ),
            cast_to=CreateEmbeddingResponse,
        )