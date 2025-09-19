import abc

from zodchy_alchemy.contracts import EngineContract
from ..config import Metadata
from ..schema import Schema


class Reader(abc.ABC):
    def __init__(self, engine: EngineContract, metadata: Metadata | None = None):
        self._schema = Schema(metadata or Metadata())
        self._engine = engine
