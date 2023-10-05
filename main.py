import logging.config
import argparse
from yandex_sdk_api.manage_vm import Zones, InstanceService
from settings import LogConfig, YC_FOLDER_ID, YC_CLOUD_ID, YC_OAUTH, YC_IAMTOKEN

logging.config.dictConfig(LogConfig)
logger = logging.getLogger('consolemode')

CREDENTIALS = dict(cloud_id=YC_CLOUD_ID, folder_id=YC_FOLDER_ID, zone=Zones.draft, oauth=YC_OAUTH)

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('--zone', default='ru-central1-b', help='Compute Engine zone to deploy to.')
    parser.add_argument('--name', default='demo-instance', help='New instance name.')
    parser.add_argument('--subnet-id', help='Subnet of the instance')
    parser.add_argument('--delete', '-d', action='store_true', default=False, help='Delete instance')
    parser.add_argument('--stop', '-s', action='store_true', default=False, help='Stop instance')
    parser.add_argument('--start', '-up', action='store_true', default=False, help='Start instance')
    parser.add_argument('--instance-id', '-id', help='Specify instance')
    parser.add_argument('--list', '-l', action='store_true', default=False, help='List instances')
    return parser.parse_args()

if __name__ == '__main__':
    arguments = parse_args()
    instance_id = 'epd73lmno3ta9f9eagtn'
    instance = InstanceService(instance_id, **CREDENTIALS)
    actions = {
        'stop': instance.stop,
        'list': instance.list,
    }

    for pair in arguments._get_kwargs():
        argument, value = pair
        action = actions.get(argument)
        if action and value:
            action()


