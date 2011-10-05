from django.conf.urls.defaults import *
from console_base.views import *
from utils import get_media
import django.conf.urls.i18n

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', index),
     (r'^static/(.+)$', get_media),
     (r'^get_menu_items/$', get_menu_items),
#     (r'^auth$', authenticate_user),
)
