import sqlalchemy
from functools import cached_property
import sqlalchemy.dialects.postgresql
from sqlalchemy_schema_factory import factory

from .config import Metadata


class Schema:
    def __init__(self, metadata: Metadata):
        self.db_metadata = sqlalchemy.MetaData(schema=metadata.schema)

    @cached_property
    def messages(self):
        return sqlalchemy.Table(
            "outbox_messages",
            self.db_metadata,
            factory.uuid_primary_key(),
            factory.string(name="name", nullable=False),
            factory.jsonb_aware(name="body", nullable=False),
            factory.jsonb_aware(name="headers", nullable=True),
        )

    @cached_property
    def tasks(self):
        return sqlalchemy.Table(
            "outbox_tasks",
            self.db_metadata,
            factory.uuid_primary_key(),
            factory.foreign_key(to_=self.messages, name="message_id", nullable=False),
            factory.string(name="dispatcher_id", nullable=False),
            factory.string(name="status", nullable=False),
            factory.datetime(name="scheduled_at", nullable=False),
            factory.jsonb_aware(name="settings", nullable=True),
        )

    @cached_property
    def logs(self):
        return sqlalchemy.Table(
            "outbox_logs",
            self.db_metadata,
            factory.uuid_primary_key(),
            factory.foreign_key(to_=self.tasks, name="task_id", nullable=False),
            factory.string(name="status", nullable=False),
            factory.jsonb_aware(name="payload", nullable=True),
        )
