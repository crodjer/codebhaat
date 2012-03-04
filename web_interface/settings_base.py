import os, djcelery
from django.conf import settings

djcelery.setup_loader()
ROOT_PATH = os.path.dirname(__file__)
# Django settings for the project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Kolkata'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '!06s2@vdj*@p+kfv((_zbi=yu1q8ts)#k(m_(p+wux9k(#oba+'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.csrf.CsrfMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = os.path.join(ROOT_PATH, 'templates')
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    'django.core.context_processors.request',        
)

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'django.contrib.comments',
    'django.contrib.humanize',
    'djcelery',
    'main',
    'ticket',
    'django.contrib.flatpages',
    #'tinymce',
    #'flatpages_tinymce',
    'registration',
    'profiles',
    'captcha',
    'valuate',
    'blog',
    'ischecker',

]

if DEBUG:
    INSTALLED_APPS.append('south')

INSTALLED_APPS = tuple(INSTALLED_APPS)

#Custom Settings
ACCOUNT_ACTIVATION_DAYS = 7
AUTH_PROFILE_MODULE = 'profiles.UserProfile'
DEFAULT_FROM_EMAIL = '"Codebhaat, IIT Kharagpur"<noreply@codebhaat.in>'
#DEFAULT_SEND_EMAIL = ['']
EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
AKISMET_API_KEY = ''


FILE_UPLOAD_MAX_MEMORY_SIZE = 1048576
MAX_UPLOAD_SIZE = 1048576
MAX_SUBMISSIONS = 100
RECAPTCHA_PUBLIC_KEY = '6LcFU8ESAAAAAC_yuc_hX-4xlPNLbI_RXzsOSjtn'
RECAPTCHA_PRIVATE_KEY = '6LcFU8ESAAAAAKmK22wpEQcdXdVEj64A9vqqYevX'



