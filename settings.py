# from subprocess import getoutput
from os import environ
from dotenv import load_dotenv

load_dotenv()
YC_TOKEN = environ.get('YC_TOKEN')
YC_CLOUD_ID = environ.get('YC_CLOUD_ID')
YC_FOLDER_ID = environ.get('YC_FOLDER_ID')
YC_OAUTH = environ.get('YC_OAUTH')

# YC_TOKEN = getoutput('yc iam create-token')
# YC_CLOUD_ID = getoutput('yc config get cloud-id')
# YC_FOLDER_ID = getoutput('yc config get folder-id')

LogConfig = {
    'version': 1,
    'formatters': {
        'details': {
            'class': 'logging.Formatter',
            'format': '%(asctime)s::%(name)s::%(lineno)d::%(levelname)s::%(message)s',
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
            'handlers': ['rotate', 'console'],
        },
        'consolemode': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
