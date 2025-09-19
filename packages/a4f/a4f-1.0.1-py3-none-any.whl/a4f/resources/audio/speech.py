from __future__ import annotations

from typing import Union
from typing_extensions import Literal

import httpx

from ... import _legacy_response
from ..._types import NOT_GIVEN, NotGiven
from ..._utils import maybe_transform
from ..._resource import SyncAPIResource
from ...types.audio import speech_create_params
from ..._base_client import make_request_options

__all__ = ["Speech"]


class Speech(SyncAPIResource):

    def create(
        self,
        *,
        input: str,
        model: Union[str],
        voice: Union[str],
        instructions: str | NotGiven = NOT_GIVEN,
        response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] | NotGiven = NOT_GIVEN,
        speed: float | NotGiven = NOT_GIVEN,
        stream_format: Literal["sse", "audio"] | NotGiven = NOT_GIVEN,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> _legacy_response.HttpxBinaryResponseContent:
        """
        Generates audio from the input text.

        Args:
          input: The text to generate audio for. The maximum length is 4096 characters.

          model:
              One of the available [TTS models](https://a4f.co/models):
              `tts-1`, `tts-1-hd` or `gpt-4o-mini-tts`.

          instructions: Control the voice of your generated audio with additional instructions. Does not
              work with `tts-1` or `tts-1-hd`.

          response_format: The format to audio in. Supported formats are `mp3`, `opus`, `aac`, `flac`,
              `wav`, and `pcm`.

          speed: The speed of the generated audio. Select a value from `0.25` to `4.0`. `1.0` is
              the default.

          stream_format: The format to stream the audio in. Supported formats are `sse` and `audio`.
              `sse` is not supported for `tts-1` or `tts-1-hd`.

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/octet-stream", **(extra_headers or {})}
        return self._post(
            "/audio/speech",
            body=maybe_transform(
                {
                    "input": input,
                    "model": model,
                    "voice": voice,
                    "instructions": instructions,
                    "response_format": response_format,
                    "speed": speed,
                    "stream_format": stream_format,
                },
                speech_create_params.SpeechCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, timeout=timeout
            ),
            cast_to=_legacy_response.HttpxBinaryResponseContent,
        )