from subprocess import getoutput
from os import environ
from dotenv import load_dotenv

load_dotenv()

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
