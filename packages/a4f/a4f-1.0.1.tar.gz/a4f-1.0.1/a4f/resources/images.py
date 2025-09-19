from __future__ import annotations

from typing import Union, Mapping, Optional, cast
from typing_extensions import Literal

from ..types import image_edit_params, image_generate_params
from .._types import NOT_GIVEN, NotGiven, FileTypes, SequenceNotStr
from .._utils import extract_files, required_args, maybe_transform, deepcopy_minimal
from .._resource import SyncAPIResource
from .._streaming import Stream
from ..types.images_response import ImagesResponse
from ..types.image_gen_stream_event import ImageGenStreamEvent
from ..types.image_edit_stream_event import ImageEditStreamEvent

__all__ = ["Images"]


class Images(SyncAPIResource):
    @required_args(["image", "prompt", "model"], ["image", "prompt", "model"])
    def edit(
        self,
        *,
        image: Union[FileTypes, SequenceNotStr[FileTypes]],
        prompt: str,
        model: Union[str] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse | Stream[ImageEditStreamEvent]:
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "model": model,
                "response_format": response_format,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"], ["image", "<array>"], ["mask"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/images/edits",
            body=maybe_transform(
                body,
                image_edit_params.ImageEditParamsStreaming
            ),
            files=files,
            cast_to=ImagesResponse,
            stream_cls=Stream[ImageEditStreamEvent],
        )

    @required_args(["prompt", "model"], ["prompt", "model"])
    def generate(
        self,
        *,
        prompt: str,
        model: Union[str] | NotGiven = NOT_GIVEN,
        n: Optional[int] | NotGiven = NOT_GIVEN,
        quality: Optional[Literal["standard", "hd"]] | NotGiven = NOT_GIVEN,
        response_format: Optional[Literal["url", "b64_json"]] | NotGiven = NOT_GIVEN,
        size: Optional[
            Literal["1024x1024", "256x256", "512x512", "1792x1024", "1024x1792"]
        ]
        | NotGiven = NOT_GIVEN,
        style: Optional[Literal["vivid", "natural"]] | NotGiven = NOT_GIVEN,
        user: str | NotGiven = NOT_GIVEN,
    ) -> ImagesResponse | Stream[ImageGenStreamEvent]:
        return self._post(
            "/images/generations",
            body=maybe_transform(
                {
                    "prompt": prompt,
                    "model": model,
                    "n": n,
                    "quality": quality,
                    "response_format": response_format,
                    "size": size,
                    "style": style,
                    "user": user,
                },
                image_generate_params.ImageGenerateParamsStreaming
            ),
            cast_to=ImagesResponse
        )