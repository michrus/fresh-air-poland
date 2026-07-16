from abc import ABC, abstractmethod
from typing import Any


class AbstractDataStorage(ABC):

    @abstractmethod
    def store_data(self, data: Any, entry_name: str) -> None:
        pass
