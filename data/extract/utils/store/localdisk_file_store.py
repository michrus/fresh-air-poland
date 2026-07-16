import logging
import json
import os
from typing import Any
from pathlib import Path

from .abstract_data_store import AbstractDataStorage


class LocaldiskJsonFileStorage(AbstractDataStorage):

    def __init__(self, directory_path: str):
        super().__init__()
        self.storage_directory_path = directory_path

    def store_data(self, data: Any, entry_name: str) -> None:
        logging.getLogger().info('Storing data: %s', entry_name)
        data_formatted_text = self._format_data_as_pretty_text(data)
        logging.getLogger().debug("Ensuring storage directory exists at: %s", self.storage_directory_path)
        Path(self.storage_directory_path).mkdir(parents=True, exist_ok=True)
        filename = f"{entry_name}.json"
        file_path = os.path.join(self.storage_directory_path, filename)
        logging.getLogger().debug("Saving data as file: %s", filename)
        with open(file_path, 'wt', encoding='utf-8') as f:
            f.write(data_formatted_text)
        logging.getLogger().info('Data storing completed.')

    @staticmethod
    def _format_data_as_pretty_text(data: dict) -> str:
        logging.getLogger().debug('Formatting data into indented pretty text.')
        data_formatted_text = json.dumps(data, indent=4)
        logging.getLogger().debug('Finished formatting data into indented pretty text.')
        return data_formatted_text
