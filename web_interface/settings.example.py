from settings_base import *

SERVER = 'server-address'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'overnite',                  
        'USER': 'username',                     
        'PASSWORD': 'pass',                  
        'HOST': SERVER,          
        'PORT': '3306',                     
    }
}

IS_API_TOKEN = ""

BROKER_HOST = SERVER
BROKER_PORT = 5672
BROKER_USER = "user"
BROKER_PASSWORD = "pass"
BROKER_VHOST = "myvhost"
