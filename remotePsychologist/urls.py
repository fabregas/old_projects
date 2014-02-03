from django.conf.urls.defaults import *
from remotepsy.views import *
from utils import get_media
import django.conf.urls.i18n

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', index),
     (r'^auth$', authenticate_user),
     (r'^change_password/$', change_password_request),
     (r'^accept_change_password/(.+)$',  accept_change_password),
     (r'^register_user/$', register_user),
     (r'^activate_user/(.+)$', activate_user),
     (r'^find_record_time/$', get_month_calendar),
     (r'^prev_month/$', get_prev_month),
     (r'^next_month/$', get_next_month),
     (r'^day_calendar/(\d{1,2}\/\d{1,2}\/\d{1,4})$', get_day_calendar),
     (r'^record/(\d{0,2})$', record_form),
     (r'^cancel_record/(\d+)$', cancel_record),
     (r'^my_records/$', get_user_records),
     (r'^get_end_time/$', get_record_endtime),
     (r'^static/(.+)$', get_media),
     (r'^logout/$', logout),
     (r'^my_balance/$', user_balance),
     (r'^my_messages/$', get_messages),
     (r'^send_message/$', send_message),
     (r'^get_liqpay_form/$', get_liqpay_form),
     (r'^liqpay_redirect/$', liqpay_redirect),
     (r'^liqpay_response/$', liqpay_response),
     (r'^services_description/$', services_description),


     (r'^manage_worktime/$', manage_worktime),
     (r'^prev_manage_month/$', get_prev_manage_month),
     (r'^next_manage_month/$', get_next_manage_month),
     (r'^manage_day/(\d{1,2}\/\d{1,2}\/\d{1,4})$', manage_day_calendar),
     (r'^manage_day/$', save_day_calendar),
     (r'^manage_record/(\d+)$', manage_record),
     (r'^admin_cancel_record/(\d+)$', admin_cancel_record),
     (r'^cancel_past_record/(\d+)$', cancel_past_record),
     (r'^manage_users/$', manage_users),
     (r'^manage_user/(\d+)$', manage_user),
     (r'^check_payment_state/(\d+)$', check_payment_state),
     (r'^manage_messages/$', manage_messages),
     (r'^admin_balance/$', admin_balance),
     (r'^admin_services/$', admin_services),
     (r'^manage_service/(\d*)$', manage_service),
     (r'^delete_service/(\d+)$', delete_service),

     (r'^i18n/', include('django.conf.urls.i18n')),

    # Example:
    # (r'^remotePsychologist/', include('remotePsychologist.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
