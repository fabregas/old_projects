import unittest
import IOTypesStructure as types
from ApplicationImplementation import *

APP = FablikManagementImplementation()
APP.start_routine({'DEBUG':True, 'FB_DATABASE_STRING':'host=127.0.0.1 user=postgres dbname=fablik_base %s','FB_DATABASE_PASSWORD':'', 'AUDIT_LEVEL':4})

insert_session = "INSERT INTO bf_activesession (session_guid, session_start, user_id) VALUES ('%s',current_timestamp,%i)"
delete_session = "DELETE FROM bf_activesession WHERE session_guid='%s'"
SESSION_ID = 'session_for_test'

APP.database.modify(insert_session % (SESSION_ID, 1))

DEP_ID = None
GROUP_ID = None
USER_ID = None


class TestFablikManagement(unittest.TestCase):
    def test_1_createDepartment(self):
        global DEP_ID, SESSION_ID
        request = types.RequestCreateDepartment()
        request.session_id = SESSION_ID
        request.parent_id = None
        request.sid = 'testSID'
        request.name = 'test department'
        request.description = 'department for test!'

        response = APP.createDepartment(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.department_id > 0, True, 'Department ID must be greater then 0')

        DEP_ID = response.department_id

    def test_2_updateDepartment(self):
        request = types.RequestUpdateDepartment()
        request.session_id = SESSION_ID
        request.department_id = DEP_ID
        request.parent_id = 1
        request.sid = 'test_in_root'
        request.name = 'test department in root'
        request.description = 'department for test (in root)!'

        response = APP.updateDepartment(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_3_deleteDepartment(self):
        request = types.RequestDeleteDepartment()
        request.session_id = SESSION_ID
        request.department_id = DEP_ID

        response = APP.deleteDepartment(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_4_createGroup(self):
        global GROUP_ID
        request = types.RequestCreateGroup()
        request.session_id = SESSION_ID
        request.parent_id = None
        request.name = 'test group'
        request.description = 'group for test!'
        request.roles_list = [1, 2]

        response = APP.createGroup(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.group_id > 0, True, 'Group ID must be greater then 0')

        GROUP_ID = response.group_id

    def test_5_updateGroup(self):
        request = types.RequestUpdateGroup()
        request.session_id = SESSION_ID
        request.parent_id = 1
        request.group_id = GROUP_ID
        request.name = 'test group mod'
        request.description = 'group for test! [mod]'
        request.roles_list = [1]

        response = APP.updateGroup(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_6_deleteGroup(self):
        request = types.RequestDeleteGroup()
        request.session_id = SESSION_ID
        request.group_id = GROUP_ID

        response = APP.deleteGroup(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_71_createUser(self):
        request = types.RequestCreateUser()
        request.session_id = SESSION_ID
        request.department_id = 1
        request.login = 'testUser'
        request.password = 'testPassword'
        request.name = 'test user'
        request.description = 'user for test!'
        request.email = ''
        request.birthday = ''
        request.group_list = [1]

        response = APP.createUser(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)
        self.assertEquals(response.user_id > 0, True, 'User ID must be greater then 0')

        global USER_ID
        USER_ID = response.user_id

    def test_72_updateUser(self):
        request = types.RequestUpdateUser()
        request.session_id = SESSION_ID
        request.department_id = 1
        request.login = 'testUser1'
        request.name = 'test user mod'
        request.description = 'user for test![mod]'
        request.email = 'test@email'
        request.birthday = '02.12.2020'
        request.group_list = [1]
        request.status = 0
        request.user_id = USER_ID

        response = APP.updateUser(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_73_changeUserPassword(self):
        request = types.RequestChangeUserPassword()
        request.session_id = SESSION_ID
        request.user_id = USER_ID
        request.new_password = 'aaaaaaaaaaa'

        response = APP.changeUserPassword(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test_74_deleteUser(self):
        request = types.RequestDeleteUser()
        request.session_id = SESSION_ID
        request.user_id = USER_ID

        response = APP.deleteUser(request)
        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test_9_close(self):
        APP.database.modify(delete_session % (SESSION_ID))
        APP.stop_routine()

