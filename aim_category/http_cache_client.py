import requests
import json
import logging
from hashlib import md5
from pathlib import Path


class HttpCacheClient():
    def __init__(self, base_url, local_file_cache='./cache'):
        self.base_url = base_url
        cache_dir_path = Path(local_file_cache).expanduser().resolve()
        cache_dir_path.mkdir(parents=True, exist_ok=True)
        self.file_cache_path = f'{str(cache_dir_path)}/{md5(base_url.encode()).hexdigest()}.json'
        self.session = requests.Session()
        self.cache = {}
        self.__load_from_local_file()

    def __load_from_local_file(self):
        try:
            with open(self.file_cache_path, 'r', encoding='utf-8') as f:
                self.cache = json.load(f)
        except FileNotFoundError:
            self.cache = {}
            pass

    def __save_to_local_file(self):
        try:
            with open(self.file_cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as ex:
            logging.error('Saving http cache for %s failed' % self.base_url)
            pass

    def post(self, payload):
        key = md5(json.dumps(payload).encode()).hexdigest()
        if key not in self.cache:
            self.cache[key] = self.session.post(self.base_url, json=payload).json(encoding='utf-8')
            self.__save_to_local_file()
        return self.cache[key]
