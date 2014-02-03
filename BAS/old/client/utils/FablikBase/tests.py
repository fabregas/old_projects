import unittest
from ApplicationImplementation import *
import IOTypesStructure as types

APP = FablikBaseImplementation()
APP.start_routine({'DEBUG':True, 'FB_DATABASE_STRING':'host=127.0.0.1 user=postgres dbname=fablik_base %s','FB_DATABASE_PASSWORD':'', 'AUDIT_LEVEL':4})
SESSION_ID = ''

class TestFablikBase(unittest.TestCase):
    def test_authenticate(self):
        request = types.RequestAuthenticate(login='fabregas', password='blik')

        response = APP.authenticate(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

        #print response.roles_list
        #self.assertNotEquals(len(response.roles_list), 0, 'Roles must be..')

        global SESSION_ID
        SESSION_ID = response.session_id
        
    def test_getMainMenu(self):
        request = types.RequestGetMainMenu(session_id=SESSION_ID, checksum='3423423')

        response = APP.getMainMenu(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test_getInterfaces(self):
        request = types.RequestGetInterfaces(session_id=SESSION_ID, checksum='3423423')

        response = APP.getInterfaces(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test_getDepartaments(self):
        request = types.RequestGetDepartaments(session_id=SESSION_ID, root_departament_id=None)

        response = APP.getDepartaments(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_getPositions(self):
        request = types.RequestGetPositions(session_id=SESSION_ID, root_position_id=None)

        response = APP.getPositions(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)



    def test_stop(self):
        APP.stop_routine()
