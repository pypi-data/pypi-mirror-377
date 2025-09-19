import typing
import datetime
from zodchy.codex.cqea import Query
from .types import TaskId, MessageId


class LogItem(typing.TypedDict):
    task_id: TaskId
    status: str
    payload: dict | None = None


class MessageItem(typing.TypedDict):
    id: MessageId
    name: str
    body: dict
    headers: dict | None = None


class TaskItem(typing.TypedDict):
    id: TaskId
    status: str
    scheduled_at: datetime.datetime
    dispatcher_id: str
    message: MessageItem
    settings: dict | None = None


# ----------------------------- Models -----------------------------
class MessageCreationModel(typing.TypedDict):
    id: MessageId
    name: str
    body: dict
    headers: dict | None = None


class TaskCreationModel(typing.TypedDict):
    id: TaskId
    message_id: MessageId
    status: str
    scheduled_at: datetime.datetime
    dispatcher_id: str
    settings: dict | None = None


class TaskUpdatingModel(typing.TypedDict):
    id: TaskId
    status: str
    scheduled_at: datetime.datetime | None = None


# ----------------------------- HandlersContracts -----------------------------
class MessageCreationWriterContract(typing.Protocol):
    async def __call__(self, message: MessageCreationModel) -> None: ...


class TasksCreationWriterContract(typing.Protocol):
    async def __call__(self, *tasks: TaskCreationModel) -> None: ...


class TasksUpdatingWriterContract(typing.Protocol):
    async def __call__(self, *tasks: TaskUpdatingModel) -> None: ...


class TasksStatusUpdatingWriterContract(typing.Protocol):
    async def __call__(self, ids: list[TaskId], status: str) -> None: ...


class TasksForStatusReaderContract(typing.Protocol):
    async def __call__(self, query: Query, assure_status: str) -> list[TaskItem]: ...
