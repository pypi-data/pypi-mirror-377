import typing
from zodchy.codex.transport import DispatcherContract, CommunicationMessage
from .contracts.messages import GetOutboxTasks, TaskStatus
from .contracts.types import TaskId, MessageId
from .contracts.storage import (
    TasksForStatusReaderContract,
    TasksStatusUpdatingWriterContract,
)
from .actors.processing import tasks_ready_for_processing_reader
from .contracts.messages import OutboxTaskForProcessingReceived


class ZodchyOutboxDispatcherRegistry:
    def __init__(self):
        self._dispatchers = {}

    def register(
        self,
        id: str,
        dispatcher: DispatcherContract,
    ):
        self._dispatchers[id] = dispatcher

    def __getitem__(self, id: str) -> DispatcherContract:
        try:
            return self._dispatchers[id]
        except KeyError:
            raise ValueError(f"Dispatcher for id {id} not found")


class ZodchyOutboxProcessor:
    def __init__(
        self,
        dispatcher_registry: ZodchyOutboxDispatcherRegistry,
        tasks_for_status_reader: TasksForStatusReaderContract,
        tasks_status_updating_writer: TasksStatusUpdatingWriterContract,
    ):
        self._dispatcher_registry = dispatcher_registry
        self._tasks_status_updating_writer = tasks_status_updating_writer
        self._tasks_for_status_reader = tasks_for_status_reader

    async def __call__(self, query: GetOutboxTasks):
        done = []
        async for message_id in self._dispatch(
            await self._get_tasks_for_processing(query),
        ):
            done.append(message_id)

        if done:
            await self._register(done)

    async def _get_tasks_for_processing(
        self,
        query: GetOutboxTasks,
    ) -> list[OutboxTaskForProcessingReceived]:
        return [
            task
            async for task in tasks_ready_for_processing_reader(
                query,
                self._tasks_for_status_reader,
            )
        ]

    async def _dispatch(
        self,
        tasks: list[OutboxTaskForProcessingReceived],
    ) -> typing.AsyncGenerator[MessageId, None]:
        for task in tasks:
            dispatcher = self._dispatcher_registry[task.dispatcher_id]
            if await dispatcher.dispatch(
                CommunicationMessage(
                    id=task.message["id"],
                    routing_key=task.message["name"],
                    body=task.message["body"],
                    headers=task.message["headers"],
                )
            ):
                yield task.message["id"]

    async def _register(
        self,
        ids: list[TaskId],
    ):
        await self._tasks_status_updating_writer(
            ids=ids,
            status=TaskStatus.PROCESSED.value,
        )
