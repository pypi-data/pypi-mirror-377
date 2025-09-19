import typing
import abc

from zodchy_alchemy.contracts import WriteConnectionContract
from zodchy_alchemy.contracts import EngineContract

from ..config import Metadata
from ..internals.schema import Schema

T = typing.TypeVar("T")


class RegistrationHandler(abc.ABC):
    def __init__(
        self, client: WriteConnectionContract | EngineContract, metadata: Metadata | None = None
    ):
        self._schema = Schema((metadata or Metadata()).schema)
        self._transaction = client if isinstance(client, WriteConnectionContract) else None
        self._engine = client if isinstance(client, EngineContract) else None


class ProcessingHandler(abc.ABC):
    def __init__(self, engine: EngineContract, metadata: Metadata | None = None):
        self._schema = Schema((metadata or Metadata()).schema)
        self._engine = engine
