import os

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

# =================================
# KAFKA SETTINGS
# =================================
KAFKA_SERVER = "{}:{}".format(os.environ.get("OSM_KAFKA_IP", "10.100.176.66"),
                              os.environ.get("OSM_KAFKA_PORT", "9094"))
KAFKA_CLIENT_ID = 'data-lcm'
KAFKA_API_VERSION = (1, 1, 0)
KAFKA_NS_MANAGER_TOPIC = 'ns'  # the selected name is used from the OSM-r5

# =================================
# OSM SETTINGS
# =================================
OSM_IP = os.environ.get("OSM_IP", "10.100.176.66")
OSM_ADMIN_CREDENTIALS = {"username": os.environ.get("OSM_USER", "admin"),
                         "password": os.environ.get("OSM_PWD", "password")}
OSM_COMPONENTS = {"UI": 'http://{}:80'.format(OSM_IP),
                  "NBI-API": 'https://{}:9999'.format(OSM_IP),
                  "RO-API": 'http://{}:9090'.format(OSM_IP)}

# =================================
# INFLUXDB SETTINGS
# =================================
# See InfluxDBClient class
INFLUX_DATABASES = {
    'default': {
        'ENGINE': 'influxdb',
        'NAME': os.environ.get("INFLUXDB_DB_NAME", 'monitoring'),
        'USERNAME': os.environ.get("INFLUXDB_USER", 'root'),
        'PASSWORD': os.environ.get("INFLUXDB_PWD", 'password'),
        'HOST': os.environ.get("PUBLIC_IP", "192.168.1.175"),
        'PORT': os.environ.get("INFLUXDB_PORT", 8086)
    }
}

# =================================
# REDIS SETTINGS
# =================================
REDIS_HOST = os.environ.get("PUBLIC_IP", "10.100.176.70")
REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
REDIS_NFVI_DB = 0
REDIS_PASSWORD = None
REDIS_EXPIRATION_SECONDS = os.environ.get("REDIS_EXPIRATION_SEC", 86400)  # default: 24 hours
# REDIS_SSL = False # default
# REDIS_SSL_KEYFILE = None # default
# REDIS_CERTFILE = None # default
# REDIS_SSL_CERT_REQS = u'required' # default
# REDIS_CA_CERTS = None # default


# ==================================
# LOGGING SETTINGS
# ==================================
# See more: https://docs.python.org/3.5/library/logging.config.html
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'detailed': {
            'class': 'logging.Formatter',
            'format': "[%(asctime)s] - [%(name)s:%(lineno)s] - [%(levelname)s] %(message)s",
        },
        'simple': {
            'class': 'logging.Formatter',
            'format': '%(name)-15s %(levelname)-8s %(processName)-10s %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'simple',
        },
        'daemon': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "{}/logs/access.log".format(PROJECT_ROOT),
            'mode': 'w',
            'formatter': 'detailed',
            'level': 'INFO',
            'maxBytes': 2024 * 2024,
            'backupCount': 5,
        },
        'errors': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': "{}/logs/error.log".format(PROJECT_ROOT),
            'mode': 'w',
            'level': 'ERROR',
            'formatter': 'detailed',
            'maxBytes': 2024 * 2024,
            'backupCount': 5,
        },
    },
    'loggers': {
        'daemon': {
            'handlers': ['daemon']
        },
        'errors': {
            'handlers': ['errors']
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['console']
    },
}
