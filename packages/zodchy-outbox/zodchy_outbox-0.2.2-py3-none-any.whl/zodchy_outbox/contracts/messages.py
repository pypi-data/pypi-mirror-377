import collections.abc
import typing
import datetime

import zodchy
from dataclasses import dataclass, fields

from .types import TaskId, MessageId, Dispatcher
from .enums import TaskStatus


class Message(typing.TypedDict):
    id: MessageId
    name: str
    body: dict
    headers: dict | None = None


@dataclass(frozen=True)
class Query(zodchy.codex.cqea.Query):
    def __iter__(
        self,
    ) -> collections.abc.Iterable[tuple[str, zodchy.codex.query.ClauseBit]]:
        for field in fields(self):
            value = getattr(self, field.name)
            if value is not zodchy.types.Empty:
                yield field.name, value


@dataclass(frozen=True, slots=True, kw_only=True)
class OutboxMessageCreated(zodchy.codex.cqea.Event):
    id: MessageId
    name: str
    body: dict
    headers: dict | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class OutboxTaskCreated(zodchy.codex.cqea.Event):
    id: TaskId
    message_id: MessageId
    dispatcher: Dispatcher
    scheduled_at: datetime.datetime
    settings: dict | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class GetOutboxTasks(Query):
    id: zodchy.operators.FilterBit[TaskId] | zodchy.types.Empty = zodchy.types.Empty
    dispatcher_id: zodchy.operators.FilterBit[str] | zodchy.types.Empty = (
        zodchy.types.Empty
    )
    status: zodchy.operators.FilterBit[str] | zodchy.types.Empty = zodchy.types.Empty
    scheduled_at: zodchy.operators.FilterBit[datetime.datetime] | zodchy.types.Empty = (
        zodchy.types.Empty
    )
    limit: zodchy.operators.SliceBit | zodchy.types.Empty = zodchy.types.Empty


@dataclass(frozen=True, slots=True, kw_only=True)
class OutboxTaskUpdated(zodchy.codex.cqea.Event):
    id: TaskId
    status: TaskStatus
    scheduled_at: datetime.datetime


@dataclass(frozen=True, slots=True, kw_only=True)
class OutboxTaskForProcessingReceived(zodchy.codex.cqea.Event):
    id: TaskId
    scheduled_at: datetime.datetime
    message: Message
    dispatcher_id: str
    settings: dict | None = None
