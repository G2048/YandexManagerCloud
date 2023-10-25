import requests
import logging.config

from abc import ABC, abstractmethod
from requests import exceptions
from settings import LogConfig, YC_IAMTOKEN, YC_CLOUD_ID, YC_FOLDER_ID

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')
logger.setLevel(10)


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
        self.API_URL = f'https://{service}.api.cloud.yandex.net/{service}/v1/'
        self.HEADERS = {'Authorization': f'Bearer {YC_IAMTOKEN}'}

    @staticmethod
    def _validateJson(jsondata):
        try:
            return jsondata()
        except exceptions.JSONDecodeError:
            return False

    def _request(self, url, params=None, method='GET', *args, **kwargs):
        url = self.API_URL + url
        self.response = requests.request(method, url=url, params=params, headers=self.HEADERS)
        logger.debug(self.response.url)
        logger.debug(self.response.status_code)

        if self.response.ok:
            data_json = self._validateJson(self.response.json)
            if data_json:
                return data_json


class YandexResourceManager(ABC, Api):
    def __init__(self):
        super().__init__('resource-manager')

    @abstractmethod
    def list(self):
        pass


class Folder(YandexResourceManager):
    def list(self):
        return self._request('folders', {'cloudId': YC_CLOUD_ID}).get('folders')


class YandexVPC(ABC, Api):
    def __init__(self):
        super().__init__('vpc')
        self.folder_id = YC_FOLDER_ID

    @abstractmethod
    def list(self):
        pass


class Network(YandexVPC):
    def list(self):
        return self._request('networks', {'folderId': self.folder_id}).get('networks')


class Address(YandexVPC):

    def list(self):
        return self._request('addresses', {'folderId': self.folder_id}).get('addresses')


class Subnet(YandexVPC):

    def list(self):
        return self._request('subnets', {'folderId': self.folder_id}).get('subnets')


class SecurityGroup(YandexVPC):
    def list(self):
        return self._request('securityGroups', {'folderId': self.folder_id}).get('securityGroups')


class YandexComputeCloud(ABC, Api):
    def __init__(self):
        super().__init__('compute')
        self.folder_id = YC_FOLDER_ID

    @abstractmethod
    def list(self):
        pass


class Images(YandexComputeCloud):
    def __init__(self):
        super().__init__()
        self.folder_id = 'standard-images'

    # "https://compute.api.cloud.yandex.net/compute/v1/images?folderId=standard-images&pageSize=1000"
    def list(self):
        return self._request('images', {'folderId': self.folder_id}).get('images')

    def getLatestByFamily(self, family):
        params = {'folderId': self.folder_id, 'family': family}
        return self._request(f'images:latestByFamily', params=params)


class Instance(YandexComputeCloud):
    def list(self):
        return self._request('instances', {'folderId': self.folder_id}).get('instances')
