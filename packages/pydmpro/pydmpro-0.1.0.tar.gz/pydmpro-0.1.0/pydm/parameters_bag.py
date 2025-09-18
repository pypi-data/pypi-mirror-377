import os
from abc import ABC, abstractmethod
from typing import Any
from underpy import Encapsulated, Immutable

class ParametersBagInterface(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        pass

class InMemoryParametersBag(Encapsulated, Immutable, ParametersBagInterface):
    def __init__(self, bag: dict[str, Any]):
        self.__bag = bag

    def get(self, key: str) -> Any:
        if key not in self.__bag:
            raise ValueError(f'Parameter {key} not found in bag.')
        return self.__bag[key]

class EnvParametersBag(ParametersBagInterface):
    def get(self, key: str) -> Any:
        return os.getenv(key)