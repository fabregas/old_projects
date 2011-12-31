# Django settings for blik_console project.
import os

from django.conf import settings
from django.conf.global_settings import *

from blik.utils.config import Config

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

SITE_PATH = os.path.dirname(os.path.abspath(__file__))

NODES_MANAGER_SUPPORT = False

DATABASE_ENGINE = 'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = Config.db_name             # Or path to database file if using sqlite3.
DATABASE_USER = Config.db_user             # Not used with sqlite3.
DATABASE_PASSWORD = Config.db_port         # Not used with sqlite3.
DATABASE_HOST = Config.db_host             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = Config.db_port             # Set to empty string for default. Not used with sqlite3.

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

MENU_DIR = os.path.join(SITE_PATH, 'menu')

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Kiev'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'
LANGUAGE_COOKIE_NAME = 'en'

SITE_MODULE = 'console'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b*(z586j2ww!@y!(!snxphw4h^$8_+c590&wa2)^%^zt$ranq#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_PATH,'templates'),
)

INSTALLED_APPS = [
    'django.contrib.sessions',
]

for item in os.listdir(SITE_PATH):
    path = os.path.join(SITE_PATH, item)
    if not os.path.isdir(path):
        continue

    if os.path.exists(os.path.join(path, '__init__.py')):
        INSTALLED_APPS.append('%s.%s'%(SITE_MODULE,item))

#discovering path to static
STATIC_PATH = [ os.path.join(SITE_PATH, 'static') ]

for item in os.listdir(SITE_PATH):
    path = os.path.join(SITE_PATH, item)
    if not os.path.isdir(path):
        continue

    static_dir = os.path.join(path, 'static')
    if os.path.exists(static_dir):
        STATIC_PATH.append(static_dir)
