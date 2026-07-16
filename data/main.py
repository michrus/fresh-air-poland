import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import asyncio

from extract.gios.stations import ExtractGIOSStationsDataAsync
from extract.utils.api.concurrent.gios.client import AsyncGIOSAPIClient
from extract.utils.store.localdisk_file_store import LocaldiskJsonFileStorage


now = datetime.now()
DATE_DIRECTORY = now.strftime('%Y-%m-%d')
TIME_DIRECTORY = now.strftime('T%H%M%S')

LOG_FORMATTER = \
    logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

LOG_PATH = os.path.join(os.curdir, 'logs', DATE_DIRECTORY, TIME_DIRECTORY)
LOG_FILENAME = f"{DATE_DIRECTORY}{TIME_DIRECTORY}"

Path(LOG_PATH).mkdir(parents=True, exist_ok=True)

FILE_HANDLER = logging.FileHandler(f"{LOG_PATH}/{LOG_FILENAME}.log")
FILE_HANDLER.setFormatter(LOG_FORMATTER)
rootLogger.addHandler(FILE_HANDLER)

CONSOLE_HANDLER = logging.StreamHandler(sys.stdout)
CONSOLE_HANDLER.setFormatter(LOG_FORMATTER)
rootLogger.addHandler(CONSOLE_HANDLER)

LOCALDISK_STORAGE_SUBPATH = ('data', 'gios', 'landing', DATE_DIRECTORY, TIME_DIRECTORY)
LOCALDISK_STORAGE_PATH = os.path.join(os.curdir, *LOCALDISK_STORAGE_SUBPATH)

STATIONS_STORAGE_PATH = os.path.join(LOCALDISK_STORAGE_PATH, 'stations')

async_gios_api_client = AsyncGIOSAPIClient()
stations_localdisk_storage = LocaldiskJsonFileStorage(
    directory_path=STATIONS_STORAGE_PATH,
)

extract_gios_stations = ExtractGIOSStationsDataAsync(
    async_api_client=async_gios_api_client,
    max_concurrent_calls=5,
    storage=stations_localdisk_storage,
)

asyncio.run(
    extract_gios_stations.extract_data()
)
