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

from settings import YC_CLOUD_ID, YC_FOLDER_ID


class InfoImage:

    def __init__(self, IApi):
        self.api = IApi
        self.images = self.api.get_images()

    def list_images(self):
        yield self.images

    def find_image(self, pattern='ubuntu-20'):
        for image in self.images:
            isoname = image.get('name')
            if isinstance(isoname, str) and isoname.startswith(pattern):
                self._image = image
                break

        return self

    def filds(self, ):
        self.id = self._image.get('id')
        self.name = self._image.get('name')
        self.created = self._image.get('createdAt')
        self.family = self._image.get('family')
        self.mindisksize = self._image.get('minDiskSize')
        self.pooled = self._image.get('pooled')
        self.status = self._image.get('status')
        self.storagesize = self._image.get('storageSize')

        return self


class InfoInstance:

    def __init__(self, instance_id):
        instance = yandex.get_compute_instance(folder_id=YC_FOLDER_ID, instance_id=instance_id)
        self.network = instance.network_interfaces[0].nat_ip_address
    #     self.id = self.instance.id
    #     self.name = self.instance.name
    #     self.hostname = self.instance.hostname
    #     self.fqdn = self.instance.fqdn
    #     self.created_at = self.instance.created_at
    #     self.ip = self.instance.network_interfaces[0]['nat_ipaddress']
    #     self.metadata = self.instance.metadata
    #     self.labels = self.instance.labels
    #     self.resources = self.instance.resources
    #     self.zone = self.instance.zone
    #
    # def status(self):
    #     self.memory = self.instance.resources[0]['memory']
    #     self.cores = self.instance.resources[0]['cores']
    #     self.core_fraction = self.instance.resources[0]['core_fraction']
    #     self.gpus = self.instance.resources[0]['gpus']
