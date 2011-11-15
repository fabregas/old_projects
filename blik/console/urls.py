from django.conf.urls.defaults import *
from console_base.views import *
from utils import get_media
import django.conf.urls.i18n
from console_base.auth import authenticate_user

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', index),
     (r'^static/(.+)$', get_media),
     (r'^get_menu_items/$', get_menu_items),
     (r'^auth/$', authenticate_user),
     (r'^clusters_list/$', get_clusters_list),
     (r'^cluster_config/(\d+)$', configure_cluster),
     (r'^change_cluster_parameters/(\d+)$', change_cluster_params),
     (r'^new_cluster/$', create_new_cluster),
     (r'^delete_cluster/(\d+)$', delete_cluster),
     (r'^cluster_nodes/(\d+)$', get_cluster_nodes),
     (r'^configure_node/(\d+)$', configure_node),
     (r'^change_node_parameters/(\d+)$', change_node_params),
     (r'^change_base_node_params/(\d+)$', change_base_node_params),
     (r'^delete_node/(\d+)$', delete_node),
     (r'^reboot_node/(\d+)$', reboot_node),
     (r'^sync_node/(\d+)$', sync_node),
     (r'^unregistered_nodes/$', unregistered_nodes),
     (r'^register_node/(\d+)$', register_node),
     (r'^operations_log/(\d+)$', get_operations_logs),
     (r'^get_operlogs_data/$', get_operlog_data),
     (r'^operation_details/(\d+)$', get_operlog_details),
     (r'^system_log/(\d+)$', get_system_logs),
     (r'^get_syslog_data/$', get_syslog_data),
     (r'^users_list/$', get_users_list),
     (r'^create_new_user/$', create_new_user),
     (r'^edit_user/(\d+)$', edit_user),
     (r'^edit_user_roles/(\d+)$', edit_user_roles),
     (r'^delete_user/(\d+)$', delete_user),
)
