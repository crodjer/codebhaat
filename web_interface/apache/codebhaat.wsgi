import os, sys
sys.path.append('/home/pankaj/codebhaat/web_interface/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'production_settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
