import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class paramType(ClassSerializer):
    name = simple.String
    value = simple.String

class simpleParamsType(ClassSerializer):
    paramsList = simple.Array(paramType)

class listedParamType(ClassSerializer):
    name = simple.String
    items = simple.Array(simple.String)

class listedParamsType(ClassSerializer):
    paramsList = simple.Array(listedParamType)

class RequestRunNGMethod(ClassSerializer):
    simpleParameters = simpleParamsType
    listedParameters = listedParamsType

class ResponseRunNGMethod(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    action_id = simple.String

