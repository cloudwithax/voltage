from __future__ import annotations

from typing import TYPE_CHECKING, List, TypedDict, Union

from typing_extensions import NotRequired

if TYPE_CHECKING:
    from .embed import EmbedPayload
    from .file import FilePayload


class ContentPayload(TypedDict):
    id: str
    by: NotRequired[str]
    name: NotRequired[str]


class MasqueradePayload(TypedDict):
    name: str
    avatar: str
    colour: str


class MessageInteractionsPayload(TypedDict):
    reactions: NotRequired[list[str]]
    restrict_reactions: NotRequired[bool]


class MessagePayload(TypedDict):
    _id: str
    channel: str
    author: str
    content: NotRequired[str]
    attachments: NotRequired[List[FilePayload]]
    edited: NotRequired[str]
    embeds: NotRequired[List[EmbedPayload]]
    mentions: NotRequired[List[str]]
    replies: NotRequired[List[str]]
    masquerade: NotRequired[MasqueradePayload]


class MessageReplyPayload(TypedDict):
    id: str
    mention: bool
