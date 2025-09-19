import abc
import typing
import sqlalchemy

from ....contracts.storage import TaskCreationModel, TaskUpdatingModel
from ....contracts.types import TaskId
from .generic import TransactionWriter, ConnectionWriter


class LogItem(typing.TypedDict):
    task_id: TaskId
    status: str
    payload: dict | None = None


class TasksOperationWriter(TransactionWriter, abc.ABC):
    async def _save_logs(self, *logs: LogItem):
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.logs).values(logs)
        )


class TasksCreationWriter(TasksOperationWriter):
    async def __call__(self, *tasks: TaskCreationModel):
        _tasks = []
        _logs = []
        for task in tasks:
            _tasks.append(
                dict(
                    id=task["id"],
                    message_id=task["message_id"],
                    dispatcher_id=task["dispatcher_id"],
                    status=task["status"],
                    scheduled_at=task["scheduled_at"],
                    settings=(
                        task["settings"]
                        if task["settings"] is not None
                        else sqlalchemy.null()
                    ),
                )
            )
            _logs.append(
                dict(
                    task_id=task["id"],
                    status=task["status"],
                    payload=dict(scheduled_at=task["scheduled_at"]),
                )
            )
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.tasks).values(_tasks)
        )
        await self._save_logs(*_logs)


class TasksUpdatingWriter(TasksOperationWriter):
    async def __call__(self, *tasks: TaskUpdatingModel):
        statuses = set()
        scheduled_ats = set()
        for task in tasks:
            statuses.add(task["status"])
            if "scheduled_at" in task:
                scheduled_ats.add(task["scheduled_at"])

        data = tasks
        if len(statuses) == 1:
            data = dict(
                status=statuses.pop(),
                scheduled_at=scheduled_ats.pop() if len(scheduled_ats) > 0 else None,
            )

        if type(data) is dict:
            await self._write_one(data, [task["id"] for task in tasks])
        elif type(data) is list:
            await self._write_many(data)

    async def _write_one(self, data: dict, ids: list[TaskId]):
        sql = (
            sqlalchemy.update(self._schema.tasks)
            .where(self._schema.tasks.c.id.in_(ids))
            .values(**{k: v for k, v in data.items() if v is not None})
        )
        await self._transaction.execute(sql)

    async def _write_many(self, data: list[dict]):
        for row in data:
            _id = row.pop("id")
            sql = (
                sqlalchemy.update(self._schema.tasks)
                .where(self._schema.tasks.c.id == _id)
                .values(row)
            )
            await self._transaction.execute(sql)


class TasksStatusUpdatingWriter(ConnectionWriter):
    async def __call__(self, ids: list[TaskId], status: str):
        async with self._engine.connect() as connection:
            await connection.execute(
                sqlalchemy.update(self._schema.tasks)
                .where(self._schema.tasks.c.id.in_(ids))
                .values(status=status)
            )
