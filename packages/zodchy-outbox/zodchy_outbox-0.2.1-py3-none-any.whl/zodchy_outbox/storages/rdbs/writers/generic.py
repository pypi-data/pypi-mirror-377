import abc

from zodchy_alchemy.contracts import WriteConnectionContract
from zodchy_alchemy.contracts import EngineContract

from ..config import Metadata
from ..schema import Schema


class Writer(abc.ABC):
    def __init__(self, metadata: Metadata | None = None):
        self._schema = Schema(metadata or Metadata())


class TransactionWriter(Writer, abc.ABC):
    def __init__(
        self, transaction: WriteConnectionContract, metadata: Metadata | None = None
    ):
        super().__init__(metadata)
        self._transaction = transaction


class ConnectionWriter(Writer, abc.ABC):
    def __init__(self, engine: EngineContract, metadata: Metadata | None = None):
        super().__init__(metadata)
        self._engine = engine
