import os, sys
sys.path.append('/home/pankaj/workspace/codebhaat/web_interface')
sys.path.append('/home/pankaj/workspace/codebhaat')

os.environ['DJANGO_SETTINGS_MODULE'] = 'web_interface.settings'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
