from __future__ import annotations

import logging
from typing import Union, Mapping, cast
from typing_extensions import overload

from ..._types import FileTypes
from ..._utils import extract_files, required_args, maybe_transform, deepcopy_minimal
from ..._resource import SyncAPIResource
from ..._streaming import Stream
from ...types.audio import transcription_create_params
from ...types.audio.transcription import Transcription
from ...types.audio.transcription_verbose import TranscriptionVerbose
from ...types.audio.transcription_stream_event import TranscriptionStreamEvent

__all__ = ["Transcriptions"]

log: logging.Logger = logging.getLogger("a4f.audio.transcriptions")


class Transcriptions(SyncAPIResource):

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str],
    ) -> Transcription: ...

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str],
    ) -> TranscriptionVerbose: ...

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str],
    ) -> str: ...

    @overload
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str],
    ) -> Stream[TranscriptionStreamEvent]:
        """
        Transcribes audio into the input language.

        Args:
          file:
              The audio file object (not file name) to transcribe, in one of these formats:
              flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, or webm.

          model: ID of the model to use. The options are `gpt-4o-transcribe`,
              `gpt-4o-mini-transcribe`, and `whisper-1` (which is powered by our open source
              Whisper V2 model).
        """


    @required_args(["file", "model"], ["file", "model"])
    def create(
        self,
        *,
        file: FileTypes,
        model: Union[str],
    ) -> str | Transcription | TranscriptionVerbose | Stream[TranscriptionStreamEvent]:
        body = deepcopy_minimal(
            {
                "file": file,
                "model": model,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(  # type: ignore[return-value]
            "/audio/transcriptions",
            body=maybe_transform(
                body,
                transcription_create_params.TranscriptionCreateParamsStreaming
            ),
            files=files
        )