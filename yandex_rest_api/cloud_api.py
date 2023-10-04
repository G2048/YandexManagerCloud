import re
import os
import json
import requests
import logging.config

from abc import ABC, abstractmethod
from requests import exceptions
from settings import LogConfig, YC_TOKEN, YC_CLOUD_ID, YC_FOLDER_ID

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('')
logger.setLevel(20)


class IApi(ABC):

    @abstractmethod
    def get_images(self):
        pass

    @abstractmethod
    def get_instances(self):
        pass


class YandexApiFactory:
    '''curl.exe -H "Authorization: Bearer $Env:YC_TOKEN"
    "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    '''

    __instance = None
    API_URL = 'https://compute.api.cloud.yandex.net/'
    IAM_TOKEN = YC_TOKEN
    HEADERS = {'Authorization': f'Bearer {IAM_TOKEN}'}

    def __new__(cls, ):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, ):
        pass

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except exceptions.JSONDecodeError as e:
            return False

    def _request(self, url, params, *args, **kwargs):
        logger.debug(f'{url}, {params=}, {self.HEADERS=}')
        response = requests.get(url=url, params=params, headers=self.HEADERS)
        logger.debug(response.status_code)

        if response.ok:
            data_json = self._validateJson(response.json)
            if data_json:
                return data_json
            else:
                return response.text


class YandexApi(IApi, YandexApiFactory):
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
