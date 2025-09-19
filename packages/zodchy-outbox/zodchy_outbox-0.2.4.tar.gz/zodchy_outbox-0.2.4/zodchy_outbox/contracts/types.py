import typing
import abc
from dataclasses import dataclass

import uuid

IdentifierType: typing.TypeAlias = uuid.UUID
TaskId: typing.TypeAlias = IdentifierType
MessageId: typing.TypeAlias = IdentifierType


@dataclass(frozen=True)
class Dispatcher(abc.ABC):
    pass


@dataclass(frozen=True)
class RabbitDispatcher(Dispatcher):
    pass
