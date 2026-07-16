import json
import logging
from datetime import datetime

import asyncio

from ..utils.api.concurrent.gios.abstract_client import AbstractAsyncGIOSAPIClient
from ..utils.api.gios.gios_params import GeneralGIOSAPIParams
from ..utils.store.abstract_data_store import AbstractDataStorage


class ExtractGIOSStationsDataAsync:

    class JobNotStartedException(Exception):
        pass

    class JobAlreadyStartedException(Exception):
        pass

    ENDPOINT = 'station/findAll'
    DATA_NAME = 'stations'

    _TOTAL_PAGES_FIELD_NAME = 'totalPages'
    _TIMESTAMP_FORMAT = '%d%m%YT%H%M%S'

    def __init__(
            self, 
            async_api_client: AbstractAsyncGIOSAPIClient, 
            max_concurrent_calls: int,
            storage: AbstractDataStorage,
            ):
        self.max_concurrent_calls = max_concurrent_calls
        self.async_api_client = async_api_client
        self.data_storage = storage
        self._job_timestamp = None

    @property
    def job_timestamp(self):
        if self._job_timestamp is None:
            raise self.JobNotStartedException()
        else:
            return self._job_timestamp

    @job_timestamp.setter
    def job_timestamp(self, value: str):
        if self._job_timestamp is None:
            try:
                datetime.strptime(value, self._TIMESTAMP_FORMAT)
                self._job_timestamp = value
            except ValueError:
                logging.error("Invalid timestamp format: %s", value)
                raise
        else:
            raise self.JobAlreadyStartedException()

    async def extract_data(self):
        self.job_timestamp = datetime.now().strftime(self._TIMESTAMP_FORMAT)
        logging.info('New data extraction began at: %s', self.job_timestamp)
        # Extract first page to get the information about amount of remaining data
        async with self.async_api_client as client:
            data = await self._extract_data_page(client=client, page=0)
        total_pages = data.get(self._TOTAL_PAGES_FIELD_NAME)
        # Create list of all page numbers remaining to extract
        page_numbers = list(range(1, total_pages))
        # Chunk the list of page numbers and extract pages in batches
        for i in range(0, len(page_numbers), self.max_concurrent_calls):
            pages_batch = page_numbers[i:i + self.max_concurrent_calls]
            await self._extract_pages_batch(pages_batch)
        logging.info('Data extraction finished.')

    async def _extract_pages_batch(self, pages_batch: list[int]) -> None:
        logging.info('Extracting pages %d - %d', pages_batch[0], pages_batch[-1])
        async with self.async_api_client as client, asyncio.TaskGroup() as tg:
            for i, p in enumerate(pages_batch):
                delay = i * 0.2
                tg.create_task(
                    self._extract_data_page(client, p, delay=delay)
                )
        logging.info('Finished extracting pages batch')

    async def _extract_data_page(
            self, client: AbstractAsyncGIOSAPIClient, page: int, delay: float = 0.0
            ) -> dict | None:
        logging.info('Extracting stations data for page %d', page)
        await asyncio.sleep(delay)
        gios_params = GeneralGIOSAPIParams(
            page=page
        )
        data = await client.fetch_gios_data(
            endpoint=self.ENDPOINT,
            gios_params=gios_params
        )
        if data:
            entry_name = f'{self.DATA_NAME}__page_{page}__{self.job_timestamp}'
            self.data_storage.store_data(
                data=data,
                entry_name=entry_name,
            )
        logging.info('Finished extracting stations data for page %d', page)
        return data

    @staticmethod
    def _format_data_as_pretty_text(data: dict) -> str:
        logging.debug('Formatting data into indented pretty text.')
        data_formatted_text = json.dumps(data, indent=4)
        logging.debug('Finished formatting data into indented pretty text.')
        return data_formatted_text

    def _write_data_to_file(self, data_formatted_text: str, file_name: str) -> None:
        logging.debug('Writing data into file.')
        logging.debug('File name: %s', file_name)
        with open(file_name, 'wt', encoding='utf-8') as f:
            f.write(data_formatted_text)
        logging.debug('Finished writing data into file.')
