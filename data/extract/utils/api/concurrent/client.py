import aiohttp
from aioretry import retry, RetryInfo

from .abstract_client import AbstractAsyncAPIClient


class AsyncAPIClient(AbstractAsyncAPIClient):
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    @staticmethod
    def _retry_policy(info: RetryInfo):
        return info.fails > 3, info.fails * 0.1

    @retry(_retry_policy)
    async def fetch_data(self, url: str, params: dict, headers: dict) -> dict:
        async with self.session.get(
                url,
                params=params,
                headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                response.raise_for_status()
