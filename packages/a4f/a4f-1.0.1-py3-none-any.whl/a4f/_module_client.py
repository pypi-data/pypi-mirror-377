from __future__ import annotations

from typing import TYPE_CHECKING
from typing_extensions import override

if TYPE_CHECKING:
    from .resources.images import Images
    from .resources.chat.chat import Chat
    from .resources.embeddings import Embeddings
    from .resources.audio.audio import Audio

from . import _load_client
from ._utils import LazyProxy


class ChatProxy(LazyProxy["Chat"]):
    @override
    def __load__(self) -> Chat:
        return _load_client().chat


class AudioProxy(LazyProxy["Audio"]):
    @override
    def __load__(self) -> Audio:
        return _load_client().audio


class ImagesProxy(LazyProxy["Images"]):
    @override
    def __load__(self) -> Images:
        return _load_client().images


class EmbeddingsProxy(LazyProxy["Embeddings"]):
    @override
    def __load__(self) -> Embeddings:
        return _load_client().embeddings


chat: Chat = ChatProxy().__as_proxied__()
audio: Audio = AudioProxy().__as_proxied__()
images: Images = ImagesProxy().__as_proxied__()
embeddings: Embeddings = EmbeddingsProxy().__as_proxied__()