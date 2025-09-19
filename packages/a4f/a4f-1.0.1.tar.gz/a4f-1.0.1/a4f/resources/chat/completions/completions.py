from __future__ import annotations

from typing import Union, Iterable, Optional, cast
from functools import partial

from .messages import (
    Messages,
)
from ...._types import NOT_GIVEN, NotGiven
from ...._utils import  maybe_transform
from ...._compat import cached_property
from ...._resource import SyncAPIResource
from ...._streaming import Stream
from ....types.chat import (
    completion_create_params,
)
from ....types.chat.chat_completion import ChatCompletion
from ....types.chat.chat_completion_chunk import ChatCompletionChunk
from ....types.chat.chat_completion_message_param import ChatCompletionMessageParam
from ....types.chat.chat_completion_tool_union_param import ChatCompletionToolUnionParam
from ....types.chat.chat_completion_stream_manager import ChatCompletionStreamManager

__all__ = ["Completions"]


class Completions(SyncAPIResource):
    @cached_property
    def messages(self) -> Messages:
        return Messages(self._client)

    def create(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str],
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolUnionParam] | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion:
        """Wrapper over the `client.chat.completions.create()` method that provides richer integrations with Python specific types
        & returns a `ParsedChatCompletion` object, which is a subclass of the standard `ChatCompletion` class.

        You can pass a pydantic model to this method and it will automatically convert the model
        into a JSON schema, send it to the API and parse the response content back into the given model.

        This method will also automatically parse `function` tool calls if:
        - You use the `a4f.pydantic_function_tool()` helper method
        - You mark your tool schema with `"strict": True`

        Example usage:
        ```py
        from pydantic import BaseModel
        from a4f import A4F


        class Step(BaseModel):
            explanation: str
            output: str


        class MathResponse(BaseModel):
            steps: List[Step]
            final_answer: str


        client = A4F()
        completion = client.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=[
                {"role": "system", "content": "You are a helpful math tutor."},
                {"role": "user", "content": "solve 8x + 31 = 2"},
            ],
            response_format=MathResponse,
        )

        message = completion.choices[0].message
        if message.parsed:
            print(message.parsed.steps)
            print("answer: ", message.parsed.final_answer)
        ```
        """

        return self._post(
            "/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "function_call": function_call,
                    "functions": functions,
                    "max_tokens": max_tokens,
                    "stream": False,
                    "temperature": temperature,
                    "tools": tools,
                },
                completion_create_params.CompletionCreateParams,
            ),
            cast_to=ChatCompletion,
            stream=False,
        )

    def stream(
        self,
        *,
        messages: Iterable[ChatCompletionMessageParam],
        model: Union[str],
        function_call: completion_create_params.FunctionCall | NotGiven = NOT_GIVEN,
        functions: Iterable[completion_create_params.Function] | NotGiven = NOT_GIVEN,
        max_tokens: Optional[int] | NotGiven = NOT_GIVEN,
        temperature: Optional[float] | NotGiven = NOT_GIVEN,
        tools: Iterable[ChatCompletionToolUnionParam] | NotGiven = NOT_GIVEN,
    ) -> ChatCompletionStreamManager:
        """Wrapper over the `client.chat.completions.create(stream=True)` method that provides a more granular event API
        and automatic accumulation of each delta.

        This also supports all of the parsing utilities that `.parse()` does.

        Unlike `.create(stream=True)`, the `.stream()` method requires usage within a context manager to prevent accidental leakage of the response:

        ```py
        with client.chat.completions.stream(
            model="gpt-4o-2024-08-06",
            messages=[...],
        ) as stream:
            for event in stream:
                if event.type == "content.delta":
                    print(event.delta, flush=True, end="")
        ```

        When the context manager is entered, a `ChatCompletionStream` instance is returned which, like `.create(stream=True)` is an iterator. The full list of events that are yielded by the iterator are outlined in [these docs](https://github.com/a4f/a4f-python/blob/main/helpers.md#chat-completions-events).

        When the context manager exits, the response will be closed, however the `stream` instance is still available outside
        the context manager.
        """

        api_request: partial[Stream[ChatCompletionChunk]] = partial(
            self.create,
            messages=messages,
            model=model,
            stream=True,
            function_call=function_call,
            functions=functions,
            max_tokens=max_tokens,
            temperature=temperature,
            tools=tools,
        )
        return ChatCompletionStreamManager(
            api_request,
            input_tools=tools,
        )