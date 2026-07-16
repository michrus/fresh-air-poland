from abc import abstractmethod

from ...gios.gios_params import GeneralGIOSAPIParams
from ..abstract_client import AbstractAsyncAPIClient


class AbstractAsyncGIOSAPIClient(AbstractAsyncAPIClient):

    @abstractmethod
    async def fetch_gios_data(self, endpoint: str, gios_params: GeneralGIOSAPIParams) -> dict:
        pass
