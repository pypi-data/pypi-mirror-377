from collections.abc import Mapping

import msgspec
from msgspec import Struct

from .events import AnyEvent
from .intents import AnyIntent


class CredentialsMessage(Struct, tag="credentials"):
    version: str
    value: dict[str, str]


class VersionMessage(Struct, tag="version"):
    value: str


class EventsMessage(Struct, tag="events"):
    value: Mapping[str, Mapping[str, list[AnyEvent]]]


class SendIntentValue(msgspec.Struct):
    c: str
    i: str
    unitId: str
    intent: AnyIntent | None


class SendIntentMessage(msgspec.Struct, tag="setIntent"):
    value: SendIntentValue


ClientMessage = CredentialsMessage | SendIntentMessage
ServerMessage = VersionMessage | EventsMessage | CredentialsMessage
