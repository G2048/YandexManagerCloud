from unittest import TestCase
from settings import YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN
from yandex_rest_api.cloud_api import Address, Network, SecurityGroup


class TestCloudConnection(TestCase):

    def test_fill_connection_cloud_variables(self):
        self.assertIsNotNone(YC_FOLDER_ID)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_OAUTH)
        self.assertIsNotNone(YC_IAMTOKEN)


class TestAddresses(TestCase):

    def setUp(self):
        self.address = Address()

    def test_list_addresses(self):
        addressees_list = self.address.list()
        self.assertEqual(200, self.address.response.status_code)
        self.assertIsNotNone(addressees_list)
        self.assertIsInstance(addressees_list, list)
        print(f'{addressees_list=}')

class TestCloudNetwork(TestCase):

    def setUp(self):
        self.network = Network()

    def test_list_networks(self):
        network_list = self.network.list()
        self.assertEqual(200, self.network.response.status_code)
        self.assertIsNotNone(network_list)
        self.assertIsInstance(network_list , list)
        print(f'{network_list=}')


class TestCloudSecurityGroup(TestCase):

    def setUp(self):
        self.security_group = SecurityGroup()

    def test_list_security_groups(self):
        security_group_list = self.security_group.list()
        self.assertEqual(200, self.security_group.response.status_code)
        self.assertIsNotNone(security_group_list)
        self.assertIsInstance(security_group_list, list)
        print(f'{security_group_list=}')