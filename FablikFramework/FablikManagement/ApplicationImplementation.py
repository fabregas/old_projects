import IOTypesStructure as IO
from FablikBaseLib.FablikErrorCodes import *
from FablikBaseLib.FablikBaseLib import FablikBaseRoutines
import sql_management as SQL
import hashlib

class FablikManagementImplementation:
    def start_routine(self, config):
        self.syncronize_application(config)

    def syncronize_application(self, config):
        self.base_lib = FablikBaseRoutines(config)
        self.database = self.base_lib.get_database_connection()

        self.debug = config.get('DEBUG',False)

    def stop_routine(self):
        del self.base_lib

    def createDepartment(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        department_id = -1

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            is_sid_exist = self.database.execute(SQL.check_department_sid % (request.sid, 0))
            if is_sid_exist:
                raise Exception (1, 'Department with SID "%s" is already exist in database'%request.sid)

            if not request.description:
                request.description = ''
            if not request.parent_id:
                request.parent_id = 'NULL'

            department_id = self.database.execute(SQL.insert_department %
                        (request.parent_id, request.sid, request.name, request.description), is_commit=True)

            department_id = department_id[0][0]
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseCreateDepartment(ret_code=err_code, ret_message=err_message, department_id=department_id)

    def updateDepartment(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            is_sid_exist = self.database.execute(SQL.check_department_sid % (request.sid, request.department_id))
            if is_sid_exist:
                raise Exception (1, 'Department with SID "%s" is already exist in database'%request.sid)

            if not request.parent_id:
                request.parent_id = 'NULL'
            self.database.modify(SQL.update_department %
                        (request.parent_id, request.sid, request.name, request.description, request.department_id))

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseUpdateDepartment(ret_code=err_code, ret_message=err_message)

    def deleteDepartment(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            child_count = self.database.execute(SQL.get_child_count % request.department_id)[0][0]
            if child_count > 0:
                raise Exception (2, 'Department has subdepartments! Deleting is impossible')

            if self.database.execute(SQL.dep_users % request.department_id)[0][0] > 0:
                raise Exception (3, 'Department has users! Deleting is impossible')

            try:
                self.database.start_transaction()
                self.database.modify(SQL.remove_dep_roles % (request.department_id))
                self.database.modify(SQL.delete_department % (request.department_id))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseDeleteDepartment(ret_code=err_code, ret_message=err_message)

    def createGroup(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        group_id = -1

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            if not request.parent_id:
                request.parent_id = 'NULL'

            try:
                self.database.start_transaction()
                group_id = self.database.execute(SQL.insert_group %
                        (request.parent_id, request.name, request.description))

                group_id = group_id[0][0]

                for role in request.roles_list:
                    self.database.modify(SQL.set_group_role % (group_id, role))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseCreateGroup(ret_code=err_code, ret_message=err_message, group_id=group_id)

    def updateGroup(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            if not request.parent_id:
                request.parent_id = 'NULL'

            try:
                self.database.start_transaction()
                self.database.modify(SQL.update_group %
                        (request.parent_id, request.name, request.description, request.group_id))

                group_id = request.group_id

                self.database.modify(SQL.remove_group_roles % (group_id))

                for role in request.roles_list:
                    self.database.modify(SQL.set_group_role % (group_id, role))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseUpdateGroup(ret_code=err_code, ret_message=err_message)

    def deleteGroup(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            try:
                self.database.start_transaction()
                self.database.modify(SQL.remove_group_users % (request.group_id))
                self.database.modify(SQL.remove_group_roles % (request.group_id))
                self.database.modify(SQL.delete_group % (request.group_id))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseUpdateGroup(ret_code=err_code, ret_message=err_message)

    def createUser(self, request):
        err_code, err_message = (FBE_OK, 'ok')
        new_user_id = -1

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            md5 = hashlib.md5()
            md5.update(request.password)
            password_md5 = md5.hexdigest()

            if not request.birthday:
                request.birthday = 'NULL'
            else:
                request.birthday = "'%s'" % request.birthday
            try:
                self.database.start_transaction()
                new_user_id = self.database.execute(SQL.insert_user %
                        (request.login, password_md5, request.name, request.email, request.birthday,
                        request.description, request.department_id))

                new_user_id = new_user_id[0][0]

                for group in request.group_list:
                    self.database.modify(SQL.set_user_group % (new_user_id, group))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseCreateUser(ret_code=err_code, ret_message=err_message, user_id=new_user_id)

    def updateUser(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            if not request.birthday:
                request.birthday = 'NULL'
            else:
                request.birthday = "'%s'" % request.birthday

            try:
                self.database.start_transaction()
                self.database.modify(SQL.update_user %
                        (request.login, request.name, request.email, request.status,
                        request.birthday, request.description, request.department_id, request.user_id))

                self.database.modify(SQL.remove_user_groups % (request.user_id))
                for group in request.group_list:
                    self.database.modify(SQL.set_user_group % (request.user_id, group))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseUpdateUser(ret_code=err_code, ret_message=err_message)

    def deleteUser(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            try:
                self.database.start_transaction()
                self.database.modify(SQL.remove_user_groups % (request.user_id))
                self.database.modify(SQL.remove_user_sessions % (request.user_id))
                self.database.modify(SQL.delete_user % (request.user_id))
            finally:
                self.database.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseDeleteUser(ret_code=err_code, ret_message=err_message)

    def changeUserPassword(self, request):
        err_code, err_message = (FBE_OK, 'ok')

        try:
            user_id = self.base_lib.auth_by_session(request.session_id)

            md5 = hashlib.md5()
            md5.update(request.new_password)
            password_md5 = md5.hexdigest()

            self.database.modify(SQL.change_user_password % (password_md5, request.user_id))
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return IO.ResponseDeleteUser(ret_code=err_code, ret_message=err_message)

