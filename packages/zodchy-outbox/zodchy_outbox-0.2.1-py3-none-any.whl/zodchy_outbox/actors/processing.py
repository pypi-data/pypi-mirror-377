import collections.abc
from ..contracts.messages import GetOutboxTasks, OutboxTaskForProcessingReceived
from ..contracts.storage import (
    TasksForStatusReaderContract,
    TasksStatusUpdatingWriterContract,
)
from ..contracts.enums import TaskStatus


async def tasks_ready_for_processing_reader(
    query: GetOutboxTasks,
    handler: TasksForStatusReaderContract,
) -> collections.abc.AsyncIterable[OutboxTaskForProcessingReceived]:
    for task in await handler(
        query=query,
        assure_status=TaskStatus.IN_PROGRESS.value,
    ):
        yield OutboxTaskForProcessingReceived(
            id=task["id"],
            message=task["message"],
            scheduled_at=task["scheduled_at"],
            dispatcher_id=task["dispatcher_id"],
            settings=task["settings"],
        )


async def processed_tasks_writer(
    tasks: list[OutboxTaskForProcessingReceived],
    tasks_status_updating_writer: TasksStatusUpdatingWriterContract,
) -> None:
    await tasks_status_updating_writer(ids=[task.id for task in tasks])
