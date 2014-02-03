import unittest
from ApplicationImplementation import *
import IOTypesStructure as types

APP = FablikBaseImplementation()
APP.start_routine({'DEBUG':True, 'FB_DATABASE_STRING':'host=127.0.0.1 user=postgres dbname=fablik_base %s','FB_DATABASE_PASSWORD':'', 'AUDIT_LEVEL':4})
SESSION_ID = ''

#FIXME: write SQL script with test data (see FablikQuery application tests )

class TestFablikBase(unittest.TestCase):
    def test_1_authenticate(self):
        request = types.RequestAuthenticate(login='fabregas', password='blik')

        response = APP.authenticate(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

        #print response.roles_list
        #self.assertNotEquals(len(response.roles_list), 0, 'Roles must be..')

        global SESSION_ID
        SESSION_ID = response.session_id

    def test_8_closeSession(self):
        request = types.RequestCloseSession(session_id=SESSION_ID)

        response = APP.closeSession(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_2_getMainMenu(self):
        request = types.RequestGetMainMenu(session_id=SESSION_ID, checksum='3423423', lang_sid='English')

        response = APP.getMainMenu(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test_3_getInterfaces(self):
        request = types.RequestGetInterfaces(session_id=SESSION_ID, checksum='3423423')

        response = APP.getInterfaces(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test_6_getForm(self):
        request = types.RequestGetForm(session_id=SESSION_ID, form_sid='testForm', checksum='dsadsa')

        response = APP.getForm(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.form_permission, 2, 'Form permission must be 2 (write permission)')
        self.assertNotEquals(len(response.form_source.encoded_data), 0, 'Form size must be greater 0')
        self.assertNotEquals(response.form_id, None, 'Form id must be not None')

        import hashlib, base64
        source = base64.decodestring(response.form_source.encoded_data)
        md5 = hashlib.md5()
        md5.update(source)
        request.checksum = md5.hexdigest()

        response = APP.getForm(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

        self.assertEquals(len(response.form_source.encoded_data), 0, 'Form size must be 0')
        self.assertNotEquals(response.form_id, None, 'Form id must be not None')

    def test_7_authenticate(self):
        request = types.RequestAuthorize(session_id=SESSION_ID, role_sid='mainAdmin')

        response = APP.authorize(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.is_authorize, 1, 'user is not has mainAdmin')


        request = types.RequestAuthorize(session_id=SESSION_ID, role_sid='FAKE Role')

        response = APP.authorize(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.is_authorize, 0, response.ret_message)


    def test_9_stop(self):
        APP.stop_routine()
