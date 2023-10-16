import os
import argparse
import sys
import traceback
import logging.config

import grpc
import yandexcloud

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from google.protobuf.json_format import MessageToDict
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
from yandex.cloud.vpc.v1.network_service_pb2_grpc import NetworkServiceStub
from yandex.cloud.vpc.v1.subnet_service_pb2_grpc import SubnetServiceStub
from yandex.cloud.vpc.v1.network_service_pb2 import ListNetworksRequest, CreateNetworkRequest, DeleteNetworkRequest
from yandex.cloud.vpc.v1.subnet_service_pb2 import ListSubnetsRequest, CreateSubnetRequest, DeleteSubnetRequest
from settings import LogConfig

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')


class ConnectToCloud:
    def __init__(self, cloud_id, folder_id, zone, oauth=None, token=None, **kwargs):
        self.CLOUD_ID = cloud_id
        self.FOLDER_ID = folder_id
        self.ZONE = zone
        self.OAUTH = oauth
        self.TOKEN = token


class YandexCloud:
    def __init__(self, connector: ConnectToCloud, *args, **kwargs):
        __interceptor = yandexcloud.RetryInterceptor(max_retry_count=10, retriable_codes=[grpc.StatusCode.UNAVAILABLE])
        self.sdk = yandexcloud.SDK(interceptor=__interceptor, token=connector.OAUTH)
        self.FOLDER_ID = connector.FOLDER_ID
        self.ZONE = connector.ZONE



@dataclass(frozen=True)
class Services:
    instance = dict(service_name='Instance', service_stub=InstanceServiceStub, service_list=ListInstancesRequest,
                    service_create=CreateInstanceRequest, service_delete=DeleteInstanceRequest
                    )
    network = dict(service_name='Network', service_stub=NetworkServiceStub, service_list=ListNetworksRequest,
                   service_create=CreateNetworkRequest, service_delete=DeleteNetworkRequest
                   )
    subnet = dict(service_name='Subnet', service_stub=SubnetServiceStub, service_list=ListSubnetsRequest,
                  service_create=CreateSubnetRequest, service_delete=DeleteSubnetRequest
                  )


class RegisterServices:
    def __init__(self, service_name, service_stub, service_list, service_create, service_delete):
        self.name = service_name
        self.stub = service_stub
        self.list = service_list
        self.create = service_create
        self.delete = service_delete
        self.meta_type = DeleteInstanceMetadata


class CreateService(YandexCloud):
    def __init__(self, service: RegisterServices, connector: ConnectToCloud):
        super().__init__(connector=connector)
        self.service = service
        self.client = self.sdk.client(self.service.stub)
        self._service_id = None

    @property
    def id(self) -> str:
        if self._service_id is None:
            raise Exception('You must to provide the service id!')
        return self._service_id

    @id.setter
    def id(self, service_id: str):
        self._service_id = service_id

    @staticmethod
    def _message_to_dict(list_response) -> dict:
        filds = list_response.ListFields()[0]
        message_value = filds[1].pop()
        return MessageToDict(message_value)

    def list(self, **kwargs) -> dict:
        # метод List работает без операций и сразу возвращает результат
        list_response = self.client.List(self.service.list(folder_id=self.FOLDER_ID, **kwargs))
        response = deepcopy(list_response)
        self.response = self._message_to_dict(response)
        return list_response

    def create(self, service_name, **kwargs):
        try:
            operation = self.client.Create(self.service.create(folder_id=self.FOLDER_ID, name=service_name, **kwargs))
            self.sdk.wait_operation_and_get_result(operation)
        except Exception as e:
            logger.error(e, exc_info=True)
            return -1
        return 0

    # CreateSubnetRequest(folder_id=self.FOLDER_ID, name=subnet_name, zone_id=self.ZONE,
    #                     network_id=network_id,
    #                     v4_cidr_blocks=[ip_area]
    #                     )

    def delete(self, **kwargs):
        operation = self.client.Delete(self.service.delete(**kwargs))
        logger.info(f'Try to delete {self.service.name} {self.id}')
        self.sdk.wait_operation_and_get_result(operation)
        # meta_type = DeleteInstanceMetadata,
        logger.info(f'Deleted {self.client.name} {self.id}')
        return 0

"""
>>> service = RegisterServices(**Services.instance)
>>> instance = CreateService(service)
>>> instance.create(**Template.simple)
>>> instance.list().id[0]
>>> instance.id = '123'
>>> instance.stop()
>>> instance.start()
"""


class InstanceService(YandexCloud):
    INSTANCES: dict[Any, Any]

    def __init__(self, instance_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

    def create(self, name, subnet_id='enptcfuhbr6prphvj0re', platform=Platforms.v1):
        self._platform = platform
        try:
            self._get_source_image()
            self._vm_metadata = self.fill_metadata()
            self._vm_resourse = self.fill_resourse()
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
    def fill_resourse(self, memory=2 * 2 ** 30, cores=2, core_fraction=20):
        # memory = 2 * 2 ** 30 = 2147483648  # 2Gb
        return {
            'memory': memory,
            'cores': cores,
            'core_fraction': core_fraction
        }

    def fill_metadata(self, **kwargs):
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
        operation = self.instance_service.Create(CreateInstanceRequest(
            name=name,
            folder_id=self.FOLDER_ID,
            zone_id=self.ZONE,
            metadata=self._vm_metadata,
            platform_id=self._platform,
            resources_spec=ResourcesSpec(**self._vm_resourse),
            boot_disk_spec=AttachedDiskSpec(
                auto_delete=True,
                disk_spec=AttachedDiskSpec.DiskSpec(
                    type_id='network-hdd',
                    size=20 * 2 ** 30,  # 2GB
                    image_id=self.source_image.id,
                )
            ),
            network_interface_specs=[NetworkInterfaceSpec(
                subnet_id=subnet_id,
                primary_v4_address_spec=PrimaryAddressSpec(
                    one_to_one_nat_spec=OneToOneNatSpec(
                        ip_version=IPV4,
                    )
                )
            ),
            ],
        )
        )
        logger.info(f'Creating virtual machine {name} initiated!')
        return operation

    @staticmethod
    def _collect_metadata() -> str:
        with open('../metadata_instances/vm_user_metadata', 'r') as file:
            file_content = file.readlines()

        file_content = ''.join(file_content)
        return file_content
