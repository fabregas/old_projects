import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class RequestAuthenticate(ClassSerializer):
    user_name = simple.String
    user_password = simple.String

class ResponseAuthenticate(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestEchoMethod(ClassSerializer):
    message = simple.String

class ResponseEchoMethod(ClassSerializer):
    ret_message = simple.String

