from abc import ABC, abstractmethod


class AbstractAsyncAPIClient(ABC):

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass

    @abstractmethod
    async def fetch_data(self, url: str, params: dict, headers: dict) -> dict:
        pass
