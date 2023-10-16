# This file is part of YandexManagerCloud.
# YandexManagerCloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YandexManagerCloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YandexManagerCloud. If not, see <https://www.gnu.org/licenses/>.

import re
import os
import json
import requests
import logging.config

from abc import ABC, abstractmethod
from requests import exceptions
from settings import LogConfig, YC_IAMTOKEN, YC_CLOUD_ID, YC_FOLDER_ID

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')
logger.setLevel(20)


class Api:
    '''curl.exe -H "Authorization: Bearer $Env:YC_TOKEN"
    "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    '''

    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance

    def __init__(self, service):
        self.API_URL = f'https://{service}.api.cloud.yandex.net/'
        self.HEADERS = {'Authorization': f'Bearer {YC_IAMTOKEN}'}

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except exceptions.JSONDecodeError:
            return False

    def _request(self, url, params, method='GET', *args, **kwargs):
        logger.debug(f'{url}, {params=}, {self.HEADERS=}')
        response = requests.request(method, url=url, params=params, headers=self.HEADERS)
        logger.debug(response.status_code)

        if response.ok:
            data_json = self._validateJson(response.json)
            if data_json:
                return data_json
            else:
                return None


class YandexInstance(Api):
    def __init__(self):
        super().__init__()


class YandexApi(Api):
    def __init__(self, ):
        super().__init__()

    # "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    def get_images(self, *, imagestype='standard-images', pagesize='100') -> list:
        PARAMS = {'folderId': imagestype, 'pageSize': pagesize}
        ready_url = f'{self.API_URL}compute/v1/images'
        images = self._request(url=ready_url, params=PARAMS).get('images')
        return images

    def get_instances(self) -> list:
        ready_url = f'{self.API_URL}compute/v1/instances'
        PARAMS = {'folderId': YC_FOLDER_ID}
        instances = self._request(url=ready_url, params=PARAMS).get('instances')
        return instances


if __name__ == '__main__':
    api = YandexApi()
    api.get_images()
    # resources = ResourcesAPI(api=YandexAPI)
    # resources.api.get_images()
