from unittest import TestCase, main
from settings import YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN
from yandex_rest_api.cloud_api import Images


class TestCloudConnection(TestCase):

    def test_fill_connection_cloud_variables(self):
        self.assertIsNotNone(YC_FOLDER_ID)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_OAUTH)
        self.assertIsNotNone(YC_IAMTOKEN)


class TestImages(TestCase):

    def setUp(self):
        self.images = Images()

    def test_list_images(self):
        images_list = self.images.list()
        self.assertEqual(200, self.images.response.status_code)
        self.assertIsNotNone(images_list)
        self.assertIsInstance(images_list, list)
        print(f'{images_list=}')

    def test_get_images_by_family(self):
        family = 'ubuntu-2004-lts'
        image = self.images.getLatestByFamily(family)
        self.assertIsNotNone(image)
        print(f'{image=}')


if __name__ == '__main__':
    main()
