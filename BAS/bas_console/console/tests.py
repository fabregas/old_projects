"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from models import *

URLS_GET = [ '/login/', '/exit/',
    '/', '/clusters/', '/server_logs/',
    '/applications/', '/application/5', '/activate_application/5',
    '/applications_logs/', '/app_log_message/1', '/applications_statistic/',
    '/deploy_application/', '/application/start/5', '/application/restart/5',
    '/application/stop/5', '/test_method/6',
    '/users/','/user_info/1', '/change_user_pwd/1', '/delete_user/6', '/new_user',
    '/cluster_1', '/modparam/1', '/modlocalparam/1', '/removeparam/1',
    '/cluster/modcluster/1', '/cluster/remcluster/1', '/cluster/modnode_1',
    '/cluster/reload/1', '/cluster/node/1', '/cluster/remnode_1',
    '/clear_messages/', '/undeploy_application/5',
    '/save_system_settings']


class SimpleTest(TestCase):
    def test_1_unauthorized_get(self):
        print '---------UNAUTHORITHED GET---------'
        for URL in URLS_GET:
            print 'GET %s'%URL
            resp = self.client.get( URL, follow=True)

            self.assertEqual(resp.status_code, 200, 'Page %s is not loaded! Returned code: %i' % (URL,resp.status_code))

            #must redirect to auth form
            self.assertEqual(resp.content.find('auth_form') > 0, True, 'Page %s must be going to auth form! But:\n%s'%(URL,resp.content))

    def test_2_authorized_get(self):
        print '---------AUTHORITHED GET---------'
        resp = self.client.post( '/login/', {'username':'fabregas','passwd':'blik'}, follow=True)

        self.assertEqual(resp.status_code, 200)

        #must redirect to /
        self.assertEqual(resp.content.find('auth_form') > 0, False)

        for URL in URLS_GET[2:]:
            print 'GET %s'%URL
            resp = self.client.get( URL, follow=True)

            self.assertEqual(resp.status_code, 200, 'Page %s is not loaded! Returned code: %i' % (URL,resp.status_code))

            #must redirect to /
            self.assertEqual(resp.content.find('auth_form') > 0, False, 'Page %s must not be going to auth form! But:\n%s'%(URL,resp.content))


