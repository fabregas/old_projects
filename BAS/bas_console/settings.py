# Django settings for blik_console project.
import os
from django.conf import settings
from django.conf.global_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

#SITE_PATH = '/home/fabregas/BAS_Console/'
SITE_PATH = os.path.abspath('.')

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'bas_db'             # Or path to database file if using sqlite3.
DATABASE_USER = 'postgres'             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

NODE_SERVICE_WSDL = 'file://%s' % os.path.join(SITE_PATH, 'static/basNodeManagement.wsdl')
SYSTEM_SERVICE_WSDL = 'file://%s' % os.path.join(SITE_PATH, 'static/basSystem.wsdl')
BAS_NODE_LOGIN = 'bas_node_agent'
BAS_NODE_PASSWORD = 'blik'

STATIC_PATH= os.path.join(SITE_PATH, 'static')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b*(z586j2ww!@y!(!snxphw4h^$8_+c590&wa2)^%^zt$ranq#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    #'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_PATH,'templates'),
    os.path.join(SITE_PATH, 'auth_app/templates'),
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.admin',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
	#'bas_admin.auth_app',
	'console'
)

FIXTURE_DIRS = (
   os.path.join(SITE_PATH,'fixtures'),
)
