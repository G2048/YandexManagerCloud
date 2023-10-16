# This file is part of YandexManagerCloud.
# YandexManagerCloud is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# YandexManagerCloud is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with YandexManagerCloud. If not, see <https://www.gnu.org/licenses/>.

import logging.config
import argparse
from yandex_sdk_api.yandex_api import Zones, ConnectToCloud, InstanceService
from settings import LogConfig, YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')

CREDENTIALS = dict(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=Zones.draft, oauth=YC_OAUTH)


def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--instance-id', '-id', help='Specify instance')
    group.add_argument('--list', '-l', action='store_true', default=False, help='List instances')
    parser.add_argument('--zone', default='ru-central1-b', help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', default='demo-instance', help='New instance name.')
    parser.add_argument('--subnet-id', help='Subnet of the instance')
    parser.add_argument('--delete', '-d', action='store_true', default=False, help='Delete instance')
    parser.add_argument('--destroy', '-da', action='store_true', default=False, help='Destroy all instances')
    parser.add_argument('--stop', '-s', action='store_true', default=False, help='Stop instance')
    parser.add_argument('--start', '-up', action='store_true', default=False, help='Start instance')
    return parser.parse_args()


class ManageVirtualMachines:
    def __init__(self, instance_id=None, **kwargs):
        self.connector: ConnectToCloud = ConnectToCloud(**CREDENTIALS)
        # super().__init__(connector=connector, **kwargs)
        self.instance = InstanceService(instance_id=instance_id, connector=self.connector)

    def all_instance_operations(self, operation, *args, **kwargs):
        self.instance.list()
        for instance_id in self.instance.INSTANCES.get('id'):
            logger.debug(f'{instance_id=}')
            instance = InstanceService(instance_id, self.connector)
            getattr(instance, operation, *args, **kwargs)()

    def destroy_all_instances(self):
        self.all_instance_operations('delete')
        # TODO: Need print name of instance

def main(arguments):
    connector = ConnectToCloud(**CREDENTIALS)
    instance = InstanceService(arguments.instance_id, connector=connector)

    actions = {
        'stop': instance.stop,
        'list': instance.list,
    }

    for pair in arguments._get_kwargs():
        argument, value = pair
        action = actions.get(argument)
        if action and value:
            instances = action().instances
            print(f'{dir(action())}')
            print(f'{instance.INSTANCES=}')

if __name__ == '__main__':
    arguments = parse_args()
    virtualmachine = ManageVirtualMachines()
    virtualmachine.destroy_all_instances()