from datetime import datetime
import os

import json
import requests
import yaml


class GIOSAPIIngest:

    def __init__(self):
        script_path = os.path.dirname(os.path.realpath(__file__))
        config_path = os.environ.get('GIOS_INGEST_CONFIG_PATH') \
            or os.path.join(script_path, 'config.yml')

        config = self._load_config(config_path=config_path)
        try:
            self.page_size = config['page_size']
            self.api_url = config['api_url']
            self.endpoints = config['endpoints']
            self.request_headers = config['request_headers']
        except KeyError as e:
            raise self.GIOSAPIIngestException(f"Failed to get '{e}' from config!")

        self.storage_path = os.environ.get('GIOS_INGEST_STORAGE_PATH') \
            or os.path.join(script_path, 'storage')

    def ingest(self):
        for ep_name, ep_path in self.endpoints.items():
            self._run_endpoint_ingest(ep_name, ep_path)

    def _load_config(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.load(f, Loader=yaml.CLoader)
        return config

    def _run_endpoint_ingest(self, endpoint_name, endpoint_path):
        
        timestamp = datetime.now().strftime(format='%Y%m%d_%H%M%S')
        url = f"{self.api_url.rstrip('/')}/{endpoint_path.lstrip('/')}"

        page = 0
        more_data = True

        while more_data:
            page += 1
            data = self._fetch_page(url)
            if data:
                total_pages = data.get('totalPages')
                self._save_data(
                    timestamp=timestamp,
                    endpoint_name=endpoint_name, 
                    page=page,
                    total_pages=total_pages,
                    data=data
                )
                
                # Set-up the next call
                links = data.get('links', {})
                url = links.get('next')
                this_page = links.get('self')
                last_page = links.get('last')
                if (this_page and last_page) and (this_page == last_page):
                    more_data = False
            else:
                more_data = False

    def _fetch_page(self, url) -> dict:
        params = {
            'size': self.page_size,
        }

        response = requests.request("GET", url, headers=self.request_headers, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            data = {}
        return data

    def _save_data(self, timestamp, endpoint_name, page, total_pages, data):
        endpoint_storage_path = os.path.join(self.storage_path, endpoint_name)
        os.makedirs(endpoint_storage_path, exist_ok=True)
        file_name = f"{endpoint_name}_{timestamp}_page_{page}_of_{total_pages}"
        save_path = os.path.join(endpoint_storage_path, file_name)
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=8)
    
    class GIOSAPIIngestException(Exception):
        pass

