#!/usr/bin/env python3
import os
import argparse
import logging.config

import grpc
import yandexcloud

from dataclasses import dataclass

from yandex.cloud.resourcemanager.v1.cloud_service_pb2 import ListCloudsRequest
from yandex.cloud.compute.v1.image_service_pb2 import GetImageLatestByFamilyRequest
from yandex.cloud.compute.v1.image_service_pb2_grpc import ImageServiceStub
from yandex.cloud.compute.v1.instance_pb2 import IPV4, Instance
from yandex.cloud.compute.v1.instance_service_pb2 import (
    CreateInstanceRequest,
    ResourcesSpec,
    AttachedDiskSpec,
    NetworkInterfaceSpec,
    PrimaryAddressSpec,
    OneToOneNatSpec,
    DeleteInstanceRequest,
    StopInstanceRequest,
    StartInstanceRequest,
    CreateInstanceMetadata,
    DeleteInstanceMetadata,
)
from yandex.cloud.compute.v1.instance_service_pb2_grpc import InstanceServiceStub

from yandex.cloud.vpc.v1.network_service_pb2 import ListNetworksRequest, CreateNetworkRequest, DeleteNetworkRequest
from yandex.cloud.vpc.v1.network_service_pb2_grpc import NetworkServiceStub

from yandex.cloud.vpc.v1.subnet_service_pb2 import ListSubnetsRequest, CreateSubnetRequest, DeleteSubnetRequest
from yandex.cloud.vpc.v1.subnet_service_pb2_grpc import SubnetServiceStub

from settings import LogConfig

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')


@dataclass
class Zones:
    core = 'ru-central1-a'
    test = 'ru-central1-b'
    draft = 'ru-central1-c'


def collect_metadata():
    with open('../metadata_instances/vm_user_metadata', 'r') as file:
        file_content = file.readlines()

    file_content = ''.join(file_content)
    logging.debug(file_content)
    return file_content


def create_instance(sdk, folder_id, zone, name, subnet_id):
    image_service = sdk.client(ImageServiceStub)
    logger.info(f'{dir(GetImageLatestByFamilyRequest)}')
    vm_metadata = {
        'serial-port-enable': '1',
        'user-data': collect_metadata(),
    }
    metadata = {'metadata-value': ''}
    vm_metadata.update(metadata)

    source_image = image_service.GetLatestByFamily(
        GetImageLatestByFamilyRequest(
            folder_id='standard-images',
            family='ubuntu-2004-lts',
            # disk_id = 'fd83gfh90hpp3sojs1r3',
        )
    )

    subnet_id = subnet_id or sdk.helpers.get_subnet(folder_id, zone)
    instance_service = sdk.client(InstanceServiceStub)
    operation = instance_service.Create(CreateInstanceRequest(
        folder_id=folder_id,
        name=name,
        resources_spec=ResourcesSpec(
            memory=2 * 2 ** 30,  # 2Gb
            cores=2,
            core_fraction=50,
        ),

        zone_id=zone,
        platform_id='standard-v1',
        boot_disk_spec=AttachedDiskSpec(
            auto_delete=True,
            disk_spec=AttachedDiskSpec.DiskSpec(
                type_id='network-hdd',
                size=20 * 2 ** 30,  # 2GB
                image_id=source_image.id,
            )
        ),

        network_interface_specs=[
            NetworkInterfaceSpec(
                subnet_id=subnet_id,
                primary_v4_address_spec=PrimaryAddressSpec(
                    one_to_one_nat_spec=OneToOneNatSpec(
                        ip_version=IPV4,
                    )
                )
            ),
        ],
        metadata=vm_metadata,
    ))

    logger.info('Creating initiated')


def create_vm():
    try:
        operation = create_instance(sdk, arguments.folder_id, arguments.zone, arguments.name, arguments.subnet_id)
        operation_result = sdk.wait_operation_and_get_result(
            operation,
            response_type=Instance,
            meta_type=CreateInstanceMetadata,
        )

        instance_id = operation_result.response.id
        logger.info(f'{instance_id=}')

    except Exception as e:
        logger.error(e)


class ConnectToCloud:

    def __init__(self, cloud_id, folder_id, zone, oauth=None, token=None, **kwargs):
        self.TOKEN = token
        self.CLOUD_ID = cloud_id
        self.FOLDER_ID = folder_id
        self.OAUTH = oauth
        self.ZONE = zone

        interceptor = yandexcloud.RetryInterceptor(max_retry_count=10, retriable_codes=[grpc.StatusCode.UNAVAILABLE])
        self.sdk = yandexcloud.SDK(interceptor=interceptor, token=self.OAUTH)
        self.instance_service = self.sdk.client(InstanceServiceStub)
        self.subnet_service = self.sdk.client(SubnetServiceStub)
        self.networks_service = self.sdk.client(NetworkServiceStub)


class Network(ConnectToCloud):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.network_id = self.sdk.helpers.find_network_id(folder_id=self.FOLDER_ID)
        # self.subnet_id = self.sdk.helpers.find_subnet_id(
        #     folder_id=self.FOLDER_ID,
        #     zone_id=self.ZONE,
        #     network_id=self.network_id,
        # )

    def list(self):
        self.networks = dict()
        networks = self.networks_service.List(ListNetworksRequest(folder_id=self.FOLDER_ID)).networks
        for network in networks:
            vault = {}
            self.networks[network.name] = vault
            vault['id'] = network.id
            vault['name'] = network.name
            vault['security_group_id'] = network.default_security_group_id
            vault['created_at'] = network.created_at
            vault['folder_id'] = network.folder_id

        return self.networks

    def create(self, network_name):
        operation = self.networks_service.Create(CreateNetworkRequest(folder_id=self.FOLDER_ID, name=network_name))
        self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Create network: {network_name}')
        return 0

    def delete(self, network_id):
        operation = self.networks_service.Delete(DeleteNetworkRequest(network_id=network_id))
        logger.info(f'Try to delete subnet {network_id}')
        self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Deleted instance {network_id}')
        return 0


class SubNet(ConnectToCloud):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list(self):
        self.subnets = dict()
        subnets = self.subnet_service.List(ListSubnetsRequest(folder_id=self.FOLDER_ID)).subnets

        for subnet in subnets:
            vault = {}
            self.subnets[subnet.name] = vault
            vault['id'] = subnet.id
            vault['name'] = subnet.name
            vault['folder_id'] = subnet.folder_id
            vault['created_at'] = subnet.created_at
            vault['description'] = subnet.description
            vault['network_id'] = subnet.network_id
            vault['zone_id'] = subnet.zone_id
            vault['ip_area'] = subnet.v4_cidr_blocks
        return self.subnets

    def create(self, subnet_name, network_id, ip_area, **kwargs):
        operation = self.subnet_service.Create(
            CreateSubnetRequest(folder_id=self.FOLDER_ID, name=subnet_name, zone_id=self.ZONE,
                                network_id=network_id,
                                v4_cidr_blocks=[ip_area]))
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Response: {response.response}')
        logger.info(f'Create subnet: {subnet_name}')
        return 0

    def delete(self, subnet_id):
        operation = self.subnet_service.Delete(DeleteSubnetRequest(subnet_id=subnet_id))
        logger.info(f'Try to delete subnet {subnet_id}')
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Response: {response.response}')
        logger.info(f'Deleted instance {subnet_id}')
        return 0


class VirtualMachine(ConnectToCloud):

    def __init__(self, instance_id, **kwargs):
        super().__init__(**kwargs)
        # self.fill_missing_arguments()
        self.instance_id = instance_id

    def fill_missing_arguments(self):
        pass

    def delete(self):
        operation = self.instance_service.Delete(DeleteInstanceRequest(instance_id=self.instance_id))
        logger.info(f'Try to delete instance {self.instance_id}')
        self.sdk.wait_operation_and_get_result(
            operation,
            meta_type=DeleteInstanceMetadata,
        )
        logger.info(f'Deleted instance {self.instance_id}')
        return 0

    def stop(self):
        operation = self.instance_service.Stop(StopInstanceRequest(instance_id=self.instance_id))
        logger.info(f'Try to stop instance {self.instance_id}')
        self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Stop instance {self.instance_id}')
        return 0

    def start(self):
        operation = self.instance_service.Start(StartInstanceRequest(instance_id=self.instance_id))
        logger.info(f'Try to start instance {self.instance_id}')
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Start instance {self.instance_id}')
        return 0


class VirtualMachinesManager(ConnectToCloud):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_instance(self):
        operation = self.instance_service.List(ListCloudsRequest(organization_id=self.FOLDER_ID))
        logger.info(f'Folder id: {self.FOLDER_ID=}')
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'List instances {response=}')
        return 0


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--zone', default='ru-central1-a', help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', default='demo-instance', help='New instance name.')
    parser.add_argument('--subnet-id', help='Subnet of the instance')
    parser.add_argument('--delete', '-d', action='store_true', default=False, help='Delete instance')
    parser.add_argument('--stop', '-s', action='store_true', default=False, help='Stop instance')
    parser.add_argument('--start', '-st', action='store_true', default=False, help='Start instance')
    parser.add_argument('--instance-id', '-id', help='Specify instance')
    parser.add_argument('--list-instances', '-l', action='store_true', default=False, help='List instances')

    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_args()
    logger.debug(f'{arguments=}')
