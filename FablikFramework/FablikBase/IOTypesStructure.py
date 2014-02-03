import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class MenuItemType(ClassSerializer):
    id = simple.Integer
    parent_id = simple.Integer
    form_sid = simple.String
    name = simple.String
    help = simple.String
    shortcut = simple.String

class InterfaceType(ClassSerializer):
    sid = simple.String
    url = simple.String

class RequestAuthenticate(ClassSerializer):
    login = simple.String
    password = simple.String

class ResponseAuthenticate(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    session_id = simple.String

class RequestAuthorize(ClassSerializer):
    session_id = simple.String
    role_sid = simple.String

class ResponseAuthorize(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    is_authorize = simple.Integer

class RequestCloseSession(ClassSerializer):
    session_id = simple.String

class ResponseCloseSession(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestGetMainMenu(ClassSerializer):
    session_id = simple.String
    lang_sid = simple.String
    checksum = simple.String

class ResponseGetMainMenu(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    menu_list = simple.Array(MenuItemType, 'item', 'menu_listArray')

class RequestGetInterfaces(ClassSerializer):
    session_id = simple.String

class ResponseGetInterfaces(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    interface_list = simple.Array(InterfaceType, 'interface', 'interface_listArray')

class RequestGetForm(ClassSerializer):
    session_id = simple.String
    form_sid = simple.String
    checksum = simple.String

class ResponseGetForm(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    form_id = simple.Integer
    form_source = binary.Attachment
    form_permission = simple.Integer

