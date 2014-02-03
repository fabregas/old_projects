from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from utils import get_media
from accounting.views import *

urlpatterns = patterns('',
    (r'^$', index),
    (r'^static/(.+)$', get_media),
    (r'^orders/$', get_static_page, {'page':'orders.html'}),
    (r'^presence/$', get_static_page, {'page':'presence.html'}),
    (r'^incspend/$', get_static_page, {'page':'inout.html'}),
    (r'^embedebts/$', get_static_page, {'page':'embedding_debts.html'}),
    (r'^get_orders/$', get_orders),
    (r'^get_all_order_items/$', get_all_order_items),
    (r'^get_orders_items/$', get_orders_items),
    (r'^update_order$', update_order),
    (r'^remove_order$', remove_order),
    (r'^sell_item$', sell_item),
    (r'^cancel_sell$', cancel_sell),
    (r'^change_item_location$', change_item_location),
    (r'^update_seller$', update_seller, {'dict_type': 'order_sellers'}),
    (r'^update_shop_seller$', update_seller, {'dict_type': 'shop_sellers'}),
    (r'^update_order_item$', update_order_item),
    (r'^update_item_price$', update_item_price),
    (r'^remove_order_item$', remove_order_item),
    (r'^get_sellers/$', get_sellers, {'dict_type': 'order_sellers'}),
    (r'^get_shop_sellers/$', get_sellers, {'dict_type': 'shop_sellers'}),
    (r'^get_json_dict/(\w+)$', get_json_dict),
    (r'^get_incspend_list/$', get_incspend_list),
    (r'^add_item_inout$', add_item_inout),
    (r'^calculate_income$', calculate_income),
    (r'^get_embedebts/$', get_embedebts),
    (r'^get_order_item/$', get_order_item),
    (r'^add_item_embedebts$', add_item_embedebts),
    (r'^remove_item_embedebts$', remove_item_embedebts),

    # Examples:
    # url(r'^$', 'inna_trade.views.home', name='home'),
    # url(r'^inna_trade/', include('inna_trade.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
