from unittest import TestCase, main
from settings import YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN
from yandex_rest_api.cloud_api import Folder


class TestCloudConnection(TestCase):

    def test_fill_connection_cloud_variables(self):
        self.assertIsNotNone(YC_FOLDER_ID)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_OAUTH)
        self.assertIsNotNone(YC_IAMTOKEN)


class TestFolder(TestCase):

    def setUp(self):
        self.folder = Folder()

    def test_list(self):
        folder_list = self.folder.list()
        self.assertEqual(200, self.folder.response.status_code)
        self.assertIsNotNone(folder_list)
        self.assertIsInstance(folder_list, list)
        print(f'{folder_list=}')

