#!/usr/bin/env python3
import os
import argparse
import sys
import traceback
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
    ListInstancesRequest,
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


class NetworkService(ConnectToCloud):

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


class SubnetService(ConnectToCloud):

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


class InstanceService(ConnectToCloud):

    def __init__(self, instance_id=None, **kwargs):
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
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Stop instance {self.instance_id}')
        return response

    def start(self):
        operation = self.instance_service.Start(StartInstanceRequest(instance_id=self.instance_id))
        logger.info(f'Try to start instance {self.instance_id}')
        response = self.sdk.wait_operation_and_get_result(operation)
        logger.info(f'Start instance {self.instance_id}')
        return response

    def list(self):
        logger.info(f'Folder id: {self.FOLDER_ID=}')
        # метод List работает без операций и сразу возвращает результат
        response = self.instance_service.List(ListInstancesRequest(folder_id=self.FOLDER_ID))
        logger.debug(f'List instances {response=}')
        return response

    def create(self, name, subnet_id='enptcfuhbr6prphvj0re'):
        try:
            self._get_source_image()
            self._vm_metadata = self._fill_metadata()
            self._vm_resourse = self._fill_resourse()
            operation = self._create_instance(name, subnet_id)
            operation_result = self.sdk.wait_operation_and_get_result(
                operation,
                response_type=Instance,
                meta_type=CreateInstanceMetadata,
            )

            instance_id = operation_result.response.id
            logger.info(f'{instance_id=}')

        except Exception as e:
            # logger.error(traceback.extract_stack())
            logger.error(e, exc_info=True)

    # For platform "standard-v1"
    # allowed core fractions: 5, 20, 100
    # allowed memory size: 1GB, 2GB, 3GB, 4GB, 5GB, 6GB, 7GB, 8GB.
    def _fill_resourse(self, memory=2 * 2 ** 30, cores=2, core_fraction=20):
        # memory = 2 * 2 ** 30 = 2147483648  # 2Gb
        return {
            'memory': memory,
            'cores': cores,
            'core_fraction': core_fraction
        }

    def _fill_metadata(self, **kwargs):
        vm_metadata = {
            'serial-port-enable': '1',
            'user-data': self._collect_metadata(),
        }

        metadata = {'metadata-value': ''}
        vm_metadata.update(metadata)
        vm_metadata.update(kwargs)
        return vm_metadata

    def _get_source_image(self):
        logger.info(f'{dir(GetImageLatestByFamilyRequest)}')
        image_service = self.sdk.client(ImageServiceStub)
        self.source_image = image_service.GetLatestByFamily(
            GetImageLatestByFamilyRequest(
                folder_id='standard-images',
                family='ubuntu-2004-lts',
                # disk_id = 'fd83gfh90hpp3sojs1r3',
            )
        )

    def _create_instance(self, name, subnet_id):

        subnet_id = self.sdk.helpers.find_subnet_id(self.FOLDER_ID, self.ZONE)
        logger.debug(f'{subnet_id=}')
        # TODO: Here is created Traceback!
        operation = self.instance_service.Create(CreateInstanceRequest(
            name=name,
            folder_id=self.FOLDER_ID,
            zone_id=self.ZONE,
            metadata=self._vm_metadata,
            platform_id='standard-v1',
            resources_spec=ResourcesSpec(**self._vm_resourse),
            boot_disk_spec=AttachedDiskSpec(
                auto_delete=True,
                disk_spec=AttachedDiskSpec.DiskSpec(
                    type_id='network-hdd',
                    size=20 * 2 ** 30,  # 2GB
                    image_id=self.source_image.id,
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
        ))
        logger.info(f'Creating virtual machine {name} initiated!')
        return operation

    @staticmethod
    def _collect_metadata() -> str:
        with open('../metadata_instances/vm_user_metadata', 'r') as file:
            file_content = file.readlines()

        file_content = ''.join(file_content)
        return file_content
