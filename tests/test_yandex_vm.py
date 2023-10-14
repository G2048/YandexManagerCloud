import unittest
from templates import Zones, Platforms, Template
from yandex_sdk_api.yandex_api import ConnectToCloud, YandexCloud, RegisterServices, CreateService, Services
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
        connector = ConnectToCloud(**CREDENTIALS)
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
        service = RegisterServices(**Services.network)
        self.network = CreateService(service, connector)
        # self.network.create(**Template.simple)
        # self.network.list().id[0]
        # self.network.id = '123'
        # self.network.stop()
        # self.network.start()

    def test_list_network(self):
        networks = self.network.list()
        print(f'{networks=}')
        # 'ByteSize', 'Clear', 'ClearExtension', 'ClearField', 'CopyFrom',
        # 'DESCRIPTOR', 'DiscardUnknownFields', 'Extensions', 'FindInitializationErrors',
        # 'FromString', 'HasExtension', 'HasField', 'IsInitialized', 'ListFields',
        # 'MergeFrom', 'MergeFromString', 'ParseFromString','RegisterExtension',
        # 'SerializePartialToString', 'SerializeToString', 'SetInParent', 'UnknownFields',
        # 'WhichOneof', '_CheckCalledFromGeneratedFile', '_ListFieldsItemKey', '_SetListener',
        print(f'{dir(networks)=}')
        print(f'{type(networks)=}')

        print(f'{dir(networks.DESCRIPTOR)=}')
        print(f'{id(networks.DESCRIPTOR.EnumValueName)=}')
        message = networks.SerializeToString()
        print(f'{message=}')
        print(f'{networks.ParseFromString(message)=}')
        # print(f'{self.network._handle_filds_todict(networks.networks)=}')
        filds = networks.ListFields()[0]
        self.assertIsInstance(filds, tuple)
        print(f'{filds[1]=}')
        print(f'{type(filds[1])=}')
        # For more see:
        # https://googleapis.dev/python/protobuf/latest/google/protobuf/internal/containers.html
        conteiner = filds[1]
        print(f'{dir(conteiner)=}')
        len_container = len(conteiner)
        self.assertGreater(len_container, 0)
        print('==================================')
        # while conteiner:
        message_value = conteiner.pop()
        print(f'{message_value=}')
        print(f'{type(message_value)=}')
        print(f'{dir(message_value)=}')
        from google.protobuf.json_format import MessageToDict
        message = MessageToDict(message_value)
        # message = MessageToDict(networks)
        self.assertIsInstance(message, dict)
        print(f'{message=}')

    def test_create_network(self):
        sub_name = 'network-test-1'
        self.network.create(sub_name)


class TestCloudSubNet(unittest.TestCase):

    def setUp(self):
        connector = ConnectToCloud(YC_CLOUD_ID, YC_FOLDER_ID, YC_ZONE, YC_OAUTH)
        service = RegisterServices(**Services.subnet)
        self.subnet = CreateService(service, connector)
        # self.network.id = self.network.list()['default']['id']

    def test_list_subnetnetwork(self):
        subnets = self.subnet.list()
        print(f'{subnets=}')
        print(f'{type(subnets.subnets[0])=}')
        print(f'{subnets.subnets[0].id=}')
        print(f'{type(subnets)=}')
        print(f'{dir(subnets)=}')
        print(f'{self.subnet.response=}')

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
