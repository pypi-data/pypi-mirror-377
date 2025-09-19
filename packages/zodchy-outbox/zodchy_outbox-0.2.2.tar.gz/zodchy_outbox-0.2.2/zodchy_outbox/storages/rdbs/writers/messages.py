import sqlalchemy

from .generic import TransactionWriter
from ....contracts.storage import MessageCreationModel
from ....contracts.types import MessageId


class MessageCreationWriter(TransactionWriter):
    async def __call__(self, message: MessageCreationModel) -> MessageId:
        await self._transaction.execute(
            sqlalchemy.insert(self._schema.messages).values(
                **{k: v for k, v in message.items() if v is not None},
            )
        )
        return message["id"]
