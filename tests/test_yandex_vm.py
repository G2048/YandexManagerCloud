import unittest
from yandex_sdk_api.yandex_api import ConnectToCloud, YandexCloud, NetworkService, SubnetService, InstanceService, Zones, Platforms
from settings import YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN

YC_ZONE = Zones.test

CREDENTIALS = dict(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=YC_ZONE, oauth=YC_OAUTH)


class TestCloudConnection(unittest.TestCase):

    def test_fill_connection_cloud_variables(self):
        self.assertIsNotNone(YC_FOLDER_ID)
        self.assertIsNotNone(YC_CLOUD_ID)
        self.assertIsNotNone(YC_ZONE)
        self.assertIsNotNone(YC_OAUTH)
        self.assertIsNotNone(YC_IAMTOKEN)

    def setUp(self):
        connector = ConnectToCloud(YC_CLOUD_ID, self.PLATFORM,
        self.cloud = YandexCloud(connector)

    def test_connect_to_cloud(self):
        print(self.cloud)

    def test_sdk(self):
        # '_channels', '_default_interceptor', 'client', 'create_operation_and_get_result', 'helpers', 'set_interceptor', 'wait_operation_and_get_result', 'waiter', 'wrappers'
        print(f'{dir(self.cloud.sdk)}')

    def test_helpers(self):
        # 'find_network_id', 'find_service_account_id', 'find_subnet_id', 'sdk'
        print(f'{dir(self.cloud.sdk.helpers)}')
        account_id = self.cloud.sdk.helpers.find_service_account_id(folder_id=YC_FOLDER_ID)
        print(f'{account_id=}')
        # network_id = self.cloud.sdk.helpers.find_network_id(folder_id=YC_FOLDER_ID)
        # print(f'{network_id=}')
        # subnet_id = self.cloud.sdk.helpers.find_subnet_id(folder_id=YC_FOLDER_ID, zone_id=YC_ZONE)
        # print(f'{subnet_id=}')


class TestCloudNetwork(unittest.TestCase):

    def setUp(self):
        connector = ConnectToCloud(YC_CLOUD_ID, YC_FOLDER_ID, YC_ZONE, YC_OAUTH)
        self.network = NetworkService(connector)

    def test_list_network(self):
        networks = self.network.list()
        # 'ByteSize', 'Clear', 'ClearExtension', 'ClearField', 'CopyFrom',
        # 'DESCRIPTOR', 'DiscardUnknownFields', 'Extensions', 'FindInitializationErrors',
        # 'FromString', 'HasExtension', 'HasField', 'IsInitialized', 'ListFields',
        # 'MergeFrom', 'MergeFromString', 'ParseFromString','RegisterExtension',
        # 'SerializePartialToString', 'SerializeToString', 'SetInParent', 'UnknownFields',
        # 'WhichOneof', '_CheckCalledFromGeneratedFile', '_ListFieldsItemKey', '_SetListener',
        print(f'{dir(networks)=}')
        list_filds = networks.ListFields()
        self.assertIsInstance(list_filds, list)
        print(f'{list_filds=}')

        list_networks = networks.networks
        self.assertGreater(len(list_networks), 0)
        # self.assertIsInstance(list_networks, list)
        print(f'{list_networks=}')

        print(f'{dir(networks.DESCRIPTOR)=}')
        print(f'{networks.DESCRIPTOR.fields=}')
        print(f'{networks.SerializeToString()=}')
        # networks = list_network.networks
        print(f'{self.network._handle_filds_todict(networks.networks)=}')
        print(f'{self.network.networks=}')
        import sys
        print(f'{sys.getsizeof(self.network.networks)=}')

    def test_create_network(self):
        sub_name = 'network-test-1'
        self.network.create(sub_name)


class TestCloudSubNet(unittest.TestCase):

    def setUp(self):
        connector = ConnectToCloud(YC_CLOUD_ID, YC_FOLDER_ID, YC_ZONE, YC_OAUTH)
        self.subnet = SubnetService(connector)
        self.network = NetworkService(connector)
        # self.network.id = self.network.list()['default']['id']

    def test_list_subnetnetwork(self):
        # subnets = self.subnet.subnets
        subnets = self.subnet.list()
        self.assertGreater(len(self.subnet.subnets), 0)
        print(f'{self.subnet.subnets["name"]=}')
        print(f'{self.subnet.subnets=}')

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


class TestCreateInstance(unittest.TestCase):
    def setUp(self):
        connector = ConnectToCloud(YC_CLOUD_ID, YC_FOLDER_ID, YC_ZONE, YC_OAUTH)
        self.instance = InstanceService(connector=connector)

    def test_sdk_instance(self):
        # 'AddOneToOneNat', 'AttachDisk', 'AttachFilesystem', 'Create', 'Delete',
        # 'DetachDisk', 'DetachFilesystem', 'Get', 'GetSerialPortOutput', 'List',
        # 'ListAccessBindings', 'ListOperations', 'Move', 'Relocate', 'RemoveOneToOneNat',
        # 'Restart', 'SetAccessBindings', 'Start', 'Stop', 'Update', 'UpdateAccessBindings',
        # 'UpdateMetadata', 'UpdateNetworkInterface'
        print(f'{dir(self.instance.instance_service)}')

    def test_create_instance(self):
        # subnet_id = 'e2l2gj8g1sl2rq8vurkt'
        name = 'test-create-grpc-vm'
        self.instance.create(name, Platforms.v1)

    def test_list_instances(self):
        inst_list_instances = self.instance.list()
        print(f'{dir(inst_list_instances)=}')
        # print(f'{inst_list_instances.ClearField()=}')
        list_instances = inst_list_instances.ListFields()[0][1]
        self.assertGreater(len(list_instances), 0)
        print(f'{len(list_instances)=}')
        instance = list_instances[1]
        print(f'{type(instance)=}')
        print(f'{instance.name=}')

    def test_stop_instance(self):
        self.instance.stop()
