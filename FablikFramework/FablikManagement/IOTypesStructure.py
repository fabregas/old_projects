import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class RequestCreateDepartment(ClassSerializer):
    session_id = simple.String
    sid = simple.String
    parent_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseCreateDepartment(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    department_id = simple.Integer

class RequestUpdateDepartment(ClassSerializer):
    session_id = simple.String
    department_id = simple.Integer
    sid = simple.String
    parent_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseUpdateDepartment(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestDeleteDepartment(ClassSerializer):
    session_id = simple.String
    department_id = simple.Integer

class ResponseDeleteDepartment(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestCreateGroup(ClassSerializer):
    session_id = simple.String
    parent_id = simple.Integer
    name = simple.String
    description = simple.String
    roles_list = simple.Array(simple.Integer, 'role', 'roles_listArray')

class ResponseCreateGroup(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    group_id = simple.Integer

class RequestUpdateGroup(ClassSerializer):
    session_id = simple.String
    group_id = simple.Integer
    parent_id = simple.Integer
    name = simple.String
    description = simple.String
    roles_list = simple.Array(simple.Integer, 'role', 'roles_listArray')

class ResponseUpdateGroup(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestDeleteGroup(ClassSerializer):
    session_id = simple.String
    group_id = simple.Integer

class ResponseDeleteGroup(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestCreateUser(ClassSerializer):
    session_id = simple.String
    login = simple.String
    name = simple.String
    email = simple.String
    description = simple.String
    birthday = simple.String
    password = simple.String
    department_id = simple.Integer
    group_list = simple.Array(simple.Integer, 'role', 'group_listArray')

class ResponseCreateUser(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    user_id = simple.Integer

class RequestUpdateUser(ClassSerializer):
    session_id = simple.String
    user_id = simple.Integer
    login = simple.String
    name = simple.String
    email = simple.String
    description = simple.String
    birthday = simple.String
    status = simple.Integer
    department_id = simple.Integer
    group_list = simple.Array(simple.Integer, 'role', 'group_listArray')

class ResponseUpdateUser(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestDeleteUser(ClassSerializer):
    session_id = simple.String
    user_id = simple.Integer

class ResponseDeleteUser(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestChangeUserPassword(ClassSerializer):
    session_id = simple.String
    user_id = simple.Integer
    new_password = simple.Integer

class ResponseChangeUserPassword(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

