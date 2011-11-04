from django.test import TestCase
from console_base.menu import get_menu
from console_base import auth, models

class MenuTest(TestCase):
    def setUp(self):
        user = models.NmUser(name='fabregas', password_hash='26c01dbc175433723c0f3ad4d5812948', email_address='blikporject@gmail.com', additional_info='')
        user.save()

        role = models.NmRole(role_sid='clusters_ro', role_name='Clusters viewer role')
        role.save()

        models.NmUserRole(user=user, role=role).save()

        cl_type = models.NmClusterType(type_sid='common', description='test')
        cl_type.save()
        cluster = models.NmCluster(cluster_sid='UT_CLUSTER_01', cluster_type=cl_type, cluster_name='Test cluster', description='', status=1, last_modifier_id=1)
        cluster.save()

        auth.cache_users()


    def test_menu_load(self):

        menu = get_menu()

        self.failUnlessEqual(len(menu)>0, True)
        self.failUnlessEqual(menu[0].has_key('children'), True)

    def test_01_authenticate(self):
        try:
            auth.authenticate('fabregas', 'test')

            auth.authenticate('fabregas1', 'blik')
        except Exception, err:
            pass
        else:
            raise Exception('Should be exception in this case')

        user = auth.authenticate('fabregas', 'blik')
        self.failUnlessEqual(user.name, 'fabregas')
        self.failUnlessEqual(user.email_address, 'blikporject@gmail.com')

        #update user
        old_pwd = user.password_hash
        user.password_hash = '8977dfac2f8e04cb96e66882235f5aba' #md5 of 'changed'
        user.save()

        auth.update_user_cache(user)

        try:
            auth.authenticate('fabregas', 'blik')
        except Exception, err:
            pass
        else:
            raise Exception('Should be exception in this case')

        user = auth.authenticate('fabregas', 'changed')
        self.failUnlessEqual(user.name, 'fabregas')

        #restore default password
        user.password_hash = old_pwd
        user.save()
        auth.update_user_cache(user)

    def authenticate(self):
        resp = self.client.post( '/auth/', {'username':'fabregas','passwd':'blik'}, follow=True)
        return resp.status_code

    def test_02_read_auth(self):
        #try getting / page, should be redirected to /auth 
        resp = self.client.get('/', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.find('auth_form') > 0, True)

        #get auth page
        resp = self.client.get('/auth/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.find('auth_form') > 0, True)

        #try authenticate
        resp = self.client.post( '/auth/', {'username':'fabregas','passwd':'blik'}, follow=True)
        self.assertEqual(resp.status_code, 200)

        #must redirect to /
        self.assertEqual(resp.content.find('auth_form') > 0, False)

    def test_03_clusters_list(self):
        #should be redirected to /auth page
        resp = self.client.get('/clusters_list', follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.find('clusters_list_table') > 0, False)

        #get empty list of clusters
        status = self.authenticate()
        self.assertEqual(status, 200)
        resp = self.client.get('/clusters_list', {'username':'fabregas','passwd':'blik'}, follow=True)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.find('clusters_list_table') > 0, True)
        self.assertEqual(resp.content.find('UT_CLUSTER_01') > 0, True)
        self.assertEqual(resp.content.find('common') > 0, True)

