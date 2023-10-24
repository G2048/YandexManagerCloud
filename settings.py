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

from os import environ
from subprocess import getoutput

YC_IAMTOKEN = getoutput('yc iam create-token')
YC_CLOUD_ID = environ.get('YC_CLOUD_ID')
YC_FOLDER_ID = environ.get('YC_FOLDER_ID')
YC_OAUTH = environ.get('YC_OAUTH')

LogConfig = {
    'version': 1,
    'formatters': {
        'details': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s::%(levelname)s::%(filename)s::%(funcName)s::%(lineno)d::%(message)s',

            'incremental': True,
        },
    },
    'handlers': {
        'rotate': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'root.log',
            'mode': 'w',
            'level': 'DEBUG',
            'maxBytes': 204800,
            'backupCount': 3,
            'formatter': 'details',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'details',
        },
    },
    'loggers': {
        '': {
            'level': 'NOTSET',
            'handlers': ['rotate'],
        },
        'consolemode': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
