from settings_base import *

SERVER = 'localhost'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'codebhaat',                  
        'USER': 'root',                     
        'PASSWORD': 'root',                  
        'HOST': SERVER,          
        'PORT': '3306',                     
    }
}

BROKER_HOST = SERVER
BROKER_PORT = 5672
BROKER_USER = "user"
BROKER_PASSWORD = "pass"
BROKER_VHOST = "myvhost"
