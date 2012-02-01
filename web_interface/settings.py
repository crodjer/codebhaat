from settings_base import *

SERVER = 'localhost'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'codebhaat',                  
        'USER': 'codebhaat',                     
        'PASSWORD': 'studcod3r',                  
        'HOST': SERVER,          
        'PORT': '3306',                     
    }
}

BROKER_HOST = SERVER
BROKER_PORT = 5672
BROKER_USER = "codebhaat"
BROKER_PASSWORD = "studecod3r"
BROKER_VHOST = "codebhaat_vhost"
