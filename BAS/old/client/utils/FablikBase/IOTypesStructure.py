import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class role(ClassSerializer):
    sid = simple.String

class departament(ClassSerializer):
    id = simple.Integer
    parent_id = simple.Integer
    name = simple.String

class position(ClassSerializer):
    id = simple.Integer
    parent_id = simple.Integer
    name = simple.String

class menu_item(ClassSerializer):
    id = simple.Integer
    parent_id = simple.Integer
    form_id = simple.Integer
    name = simple.String
    help = simple.String
    shortcut = simple.String

class interface(ClassSerializer):
    sid = simple.String
    url = simple.String

class RequestAuthenticate(ClassSerializer):
    login = simple.String
    password = simple.String

class ResponseAuthenticate(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    session_id = simple.String
    roles_list = simple.Array(role)

class RequestGetMainMenu(ClassSerializer):
    session_id = simple.String
    checksum = simple.String

class ResponseGetMainMenu(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    menu_list = simple.Array(menu_item)

class RequestGetInterfaces(ClassSerializer):
    session_id = simple.String
    checksum = simple.String

class ResponseGetInterfaces(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    interface_list = simple.Array(interface)

class RequestGetDepartaments(ClassSerializer):
    session_id = simple.String
    root_departament_id = simple.String

class ResponseGetDepartaments(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    departament_list = simple.Array(departament)

class RequestGetPositions(ClassSerializer):
    session_id = simple.String
    root_position_id = simple.Integer

class ResponseGetPositions(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    position_list = simple.Array(position)

class RequestAppendPosition(ClassSerializer):
    session_id = simple.String
    parent_position_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseAppendPosition(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    position_id = simple.Integer

class RequestUpdatePosition(ClassSerializer):
    session_id = simple.String
    position_id = simple.Integer
    parent_position_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseUpdatePosition(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestDeletePosition(ClassSerializer):
    session_id = simple.String
    position_id = simple.Integer

class ResponseDeletePosition(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestAppendDepartament(ClassSerializer):
    session_id = simple.String
    parent_departament_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseAppendDepartament(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    departament_id = simple.Integer

class RequestUpdateDepartament(ClassSerializer):
    session_id = simple.String
    departament_id = simple.Integer
    parent_departament_id = simple.Integer
    name = simple.String
    description = simple.String

class ResponseUpdateDepartament(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestDeleteDepartament(ClassSerializer):
    session_id = simple.String
    departament_id = simple.Integer

class ResponseDeleteDepartament(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

