from django.conf.urls.defaults import *

from auth_app.views import auth_user
from console.base_views import *
from console.topology_views import *
from console.applications_views import *
from utils import get_media
# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
     (r'^$', index),
     (r'^login/$', auth_user),
     (r'^about/$', get_about),
     (r'^users/$', get_users),
     (r'^new_user/$', new_user),
     (r'^user_info/(\d+)$', get_user),
     (r'^change_user_pwd/(\d+)$', change_user_password),
     (r'^delete_user/(\d+)$', delete_user),
     (r'^exit/$', exit),
     (r'^clusters/$',clusters_list),
     (r'^server_logs/(\d*)$', get_server_log),
     (r'^applications_logs/(\d*)$', get_applications_log),
     (r'^app_log_message/(\d*)$', get_log_message),
     (r'^applications_statistic/$', get_application_statistic),
     (r'^clear_statistic/$', clear_statistic),
     (r'^clear_messages/$', clear_messages),
     (r'^applications/(\d*)$',get_applications),
     (r'^application/(\d+)$',application_index),
     (r'^sharedlibrary/(\d+)$',sharedlibrary_index),
     (r'^undeploy_application/(\d+)$', undeploy_application),
     (r'^activate_application/(\d+)$', activate_application),
     (r'^deploy_application/$', deploy_application),
     (r'^application/start/(\d+)$', start_application),
     (r'^application/restart/(\d+)$', restart_application),
     (r'^application/stop/(\d+)$', stop_application),
     (r'^test_method/(\d+)$', test_application_method),
     (r'^save_method_logging/$', save_method_logging),
     (r'^cluster_(\d+)$',cluster_index),
     (r'^get_nodes_states/(\d+)$',get_nodes_states),
     (r'^get_application_state/(\d*)$',get_application_state),
     (r'^save_system_settings$', save_system_settings),
     (r'^static/(.+)$', get_media),
     (r'^modparam/(\d*)$', modify_global_app_param),
     (r'^modlocalparam/(\d*)$', modify_local_app_param),
     (r'^removeparam/(\d+)$', remove_config_param),
     (r'^cluster/modcluster/(\d*)$', modify_cluster),
     (r'^cluster/remcluster/(\d+)$', remote_cluster),
     (r'^cluster/modnode_(\d*)$', modify_node),
     (r'^cluster/remnode_(\d+)$', remote_node),
     (r'^cluster/reload/(\d+)$', reload_cluster),
     (r'^cluster/node/(\d+)$', get_node)

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
