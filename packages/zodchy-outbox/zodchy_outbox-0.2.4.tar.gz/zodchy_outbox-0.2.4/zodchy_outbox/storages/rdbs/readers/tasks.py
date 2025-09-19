import sqlalchemy
from zodchy.codex.cqea import Query
from zodchy_alchemy import QueryAssembler
from zodchy_alchemy.adapters.cqea import QueryAdapter

from .generic import Reader


class TasksForStatusReader(Reader):
    async def __call__(self, query: Query, assure_status: str):
        async with self._engine.begin() as connection:
            sql_query = sqlalchemy.select(
                self._schema.tasks.c.id,
                self._schema.tasks.c.scheduled_at,
                self._schema.tasks.c.dispatcher_id,
                self._schema.tasks.c.message_id,
                self._schema.tasks.c.status,
                self._schema.tasks.c.settings,
                self._schema.messages.c.name.label("message__name"),
                self._schema.messages.c.body.label("message__body"),
                self._schema.messages.c.headers.label("message__headers"),
            ).join(
                self._schema.messages,
                self._schema.tasks.c.message_id == self._schema.messages.c.id,
                isouter=True,
            )
            adapter = QueryAdapter(
                default_table=self._schema.tasks,
            )
            assembler = QueryAssembler(sql_query)
            sql = assembler(*adapter(query))
            stream = await connection.execute(sql)
            result = [
                dict(
                    id=row.id,
                    message=dict(
                        id=row.message_id,
                        name=row.message__name,
                        body=row.message__body,
                        headers=row.message__headers,
                    ),
                    dispatcher_id=row.dispatcher_id,
                    settings=row.settings,
                    status=row.status,
                    scheduled_at=row.scheduled_at,
                )
                for row in stream
            ]
            if result:
                await connection.execute(
                    sqlalchemy.update(self._schema.tasks)
                    .where(self._schema.tasks.c.id.in_([task["id"] for task in result]))
                    .values(status=assure_status)
                )
            return result
