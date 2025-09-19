import datetime
import typing

T = typing.TypeVar("T")


from zodchy.codex.transport import DispatcherContract, CommunicationMessage

from .contracts.messages import GetOutboxTasks, TaskStatus
from .contracts.storage import TaskUpdatingModel
from .contracts.storage import (
    TasksUpdatingHandlerContract, 
    TasksForStatusHandlerContract, 
    LogsCreationHandlerContract
)
from .actors.processing import tasks_ready_for_dispatch_reader
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
        

class ZodchyOutboxProcessor(typing.Generic[T]):
    def __init__(
        self, 
        dispatcher_registry: ZodchyOutboxDispatcherRegistry,
        tasks_updating_handler: TasksUpdatingHandlerContract,
        tasks_for_status_handler: TasksForStatusHandlerContract,
        logs_creation_handler: LogsCreationHandlerContract,
    ):
        self._dispatcher_registry = dispatcher_registry
        self._tasks_updating_handler = tasks_updating_handler
        self._tasks_for_status_handler = tasks_for_status_handler
        self._logs_creation_handler = logs_creation_handler
        
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
            async for task in tasks_ready_for_dispatch_reader(
                query,
                self._tasks_for_status_handler,
            )
        ]    
    
    async def _dispatch(
        self, 
        messages: list[OutboxTaskForProcessingReceived],
    ) -> typing.AsyncGenerator[T, None]:
        for message in messages:
            dispatcher = self._dispatcher_registry[message.handler_id]
            if await dispatcher.dispatch(
                CommunicationMessage(
                    id=message.id,
                    body=message.message_payload,
                    headers=message.handler_settings,
                )
            ):
                yield message.id


    async def _register(
        self,
        messages: list[CommunicationMessage[T]],
    ):
        await self._tasks_updating_handler(
            *(
                TaskUpdatingModel(id=message.id, status=TaskStatus.PROCESSED.value, scheduled_at=datetime.datetime.utcnow())
                for message in messages
            )
        )    
        