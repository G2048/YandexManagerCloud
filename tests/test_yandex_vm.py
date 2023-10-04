import unittest
from yandex_sdk_api.manage_vm import ConnectToCloud, Network, SubNet, Zones
from settings import YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_TOKEN

YC_FOLDER_ID = 'b1gkdjgddfq76nbvmjhk'
YC_CLOUD_ID = 'b1gda5oouc6shavprkge'
YC_ZONE = Zones.core


class TestCloudConnection(unittest.TestCase):

    def test_fill_connection_cloud_variables(self):
        self.assertIsNotNone(YC_FOLDER_ID)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_ZONE)
        self.assertIsNotNone(YC_OAUTH)
        # self.assertIsNotNone(YC_TOKEN)

    def setUp(self):
        self.cloud = ConnectToCloud(YC_CLOUD_ID, YC_FOLDER_ID, YC_ZONE, YC_OAUTH)

    def test_connect_to_cloud(self):
        print(self.cloud)

    def test_sdk(self):
        # '_channels', '_default_interceptor', 'client', 'create_operation_and_get_result', 'helpers', 'set_interceptor', 'wait_operation_and_get_result', 'waiter', 'wrappers'
        print(f'{dir(self.cloud.sdk)}')

    def test_sdk_client(self):
        # 'AddOneToOneNat', 'AttachDisk', 'AttachFilesystem', 'Create', 'Delete',
        # 'DetachDisk', 'DetachFilesystem', 'Get', 'GetSerialPortOutput', 'List',
        # 'ListAccessBindings', 'ListOperations', 'Move', 'Relocate', 'RemoveOneToOneNat',
        # 'Restart', 'SetAccessBindings', 'Start', 'Stop', 'Update', 'UpdateAccessBindings',
        # 'UpdateMetadata', 'UpdateNetworkInterface'
        print(f'{dir(self.cloud.instance_service)}')

    def test_helpers(self):
        # 'find_network_id', 'find_service_account_id', 'find_subnet_id', 'sdk'
        print(f'{dir(self.cloud.sdk.helpers)}')
        account_id = self.cloud.sdk.helpers.find_service_account_id(folder_id=YC_FOLDER_ID)
        print(f'{account_id=}')
        network_id = self.cloud.sdk.helpers.find_network_id(folder_id=YC_FOLDER_ID)
        print(f'{network_id=}')
        # subnet_id = self.cloud.sdk.helpers.find_subnet_id(folder_id=YC_FOLDER_ID, zone_id=YC_ZONE)
        # print(f'{subnet_id=}')


class TestCloudNetwork(unittest.TestCase):

    def setUp(self):
        self.network = Network(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=YC_ZONE, oauth=YC_OAUTH)

    def test_list_network(self):
        list_network = self.network.list()
        # 'ByteSize', 'Clear', 'ClearExtension', 'ClearField', 'CopyFrom',
        # 'DESCRIPTOR', 'DiscardUnknownFields', 'Extensions', 'FindInitializationErrors',
        # 'FromString', 'HasExtension', 'HasField', 'IsInitialized', 'ListFields',
        # 'MergeFrom', 'MergeFromString', 'ParseFromString','RegisterExtension',
        # 'SerializePartialToString', 'SerializeToString', 'SetInParent', 'UnknownFields',
        # 'WhichOneof', '_CheckCalledFromGeneratedFile', '_ListFieldsItemKey', '_SetListener',
        # print(f'{dir(list_network)}')
        # print(f'{list_network.ListFields()}')
        # networks = list_network.networks
        self.assertGreater(len(list_network), 0)
        # print(f'{networks=}')
        # type(networks[0])=<class 'yandex.cloud.vpc.v1.network_pb2.Network'>
        print(f'{list_network=}')
        # print(f'{list_network=}')
        # print(f'{networks[0].id=}')
        # print(f'{networks[1].id=}')
        # print(f'{networks[0].name=}')
        # print(f'{networks[1].name=}')
        # print(f'{networks[0].default_security_group_id=}')
        # print(f'{networks[0].created_at=}')
        # print(f'{networks[0].folder_id=}')

    def test_create_network(self):
        sub_name = 'network-test-1'
        self.network.create(sub_name)


class TestCloudSubNet(unittest.TestCase):

    def setUp(self):
        self.subnet = SubNet(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=YC_ZONE, oauth=YC_OAUTH)
        self.network = Network(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=YC_ZONE, oauth=YC_OAUTH)
        self.network.id = self.network.list()['default']['id']

    def test_list_network(self):
        # subnets = self.subnet.subnets
        subnets = self.subnet.list()
        self.assertGreater(len(subnets), 0)
        print(f'{subnets["subnet1"]}')
        print(f'{subnets}')
        # print(f'{subnets=}')
        # print(f'{subnets[0].id=}')
        # print(f'{subnets[0].name=}')
        # print(f'{subnets[0].created_at=}')
        # print(f'{subnets[0].folder_id=}')
        # print(f'{subnets[0].network_id=}')
        # print(f'{subnets[0].zone_id=}')
        # print(f'{subnets[0].v4_cidr_blocks[0]=}')

    def test_create_subnet(self):
        sub_name = 'subnet-test-1'
        network_id = self.network.id
        print(f'{network_id=}')
        print(f'{type(network_id)}')
        ip_area = '10.10.10.0/24'
        # v4_cidr_blocks = "192.169.10.1/24"
        # v4_cidr_blocks = '10.0.0.1/22'
        self.subnet.create(sub_name, network_id, ip_area)

    def test_delete_subnet(self):
        subnet_list = self.subnet.list()
        # Maybe I want to use setattr ?
        subnet_id = subnet_list['subnet-test-1']['id']
        self.subnet.delete(subnet_id)
