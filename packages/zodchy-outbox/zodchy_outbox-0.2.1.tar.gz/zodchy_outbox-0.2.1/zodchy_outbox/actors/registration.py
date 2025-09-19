from .. import contracts


async def message_registration_writer(
    data: contracts.messages.OutboxMessageCreated,
    message_creation_writer: contracts.storage.MessageCreationWriterContract,
) -> None:
    await message_creation_writer(
        dict(
            id=data.id,
            name=data.name,
            body=data.body,
            headers=data.headers,
        )
    )


async def task_registration_writer(
    data: contracts.messages.OutboxTaskCreated,
    tasks_creation_writer: contracts.storage.TasksCreationWriterContract,
) -> None:
    dispatcher_id = (
        type(data.dispatcher).__name__.replace("Dispatcher", "").lower()
    )
    await tasks_creation_writer(
        dict(
            id=data.id,
            message_id=data.message_id,
            status=contracts.enums.TaskStatus.SCHEDULED.value,
            scheduled_at=data.scheduled_at,
            dispatcher_id=dispatcher_id,
            settings=data.settings,
        )
    )
