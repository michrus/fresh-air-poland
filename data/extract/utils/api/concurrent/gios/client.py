from .abstract_client import AbstractAsyncGIOSAPIClient
from ..client import AsyncAPIClient
from ...gios.gios_params import GeneralGIOSAPIParams


class AsyncGIOSAPIClient(AbstractAsyncGIOSAPIClient, AsyncAPIClient):

    BASE_URL = 'https://api.gios.gov.pl/pjp-api/v1/rest'
    HEADERS = {
        'accept': 'application/ld+json',
    }

    async def fetch_gios_data(self, endpoint: str, gios_params: GeneralGIOSAPIParams) -> dict:
        url = f"{self.BASE_URL}/{endpoint}"
        params = {
            'page': gios_params.page,
        }
        if gios_params.size is not None:
            params['size'] = gios_params.size
        return await super().fetch_data(
            url=url,
            params=params,
            headers=self.HEADERS
        )
