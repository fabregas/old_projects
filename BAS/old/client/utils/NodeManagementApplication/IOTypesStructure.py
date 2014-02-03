import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class AuthType(ClassSerializer):
    login = simple.String
    password = simple.String

class RequestStartApplication(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseStartApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestRestartApplication(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseRestartApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestStopApplication(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseStopApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestLoadLibrary(ClassSerializer):
    auth = AuthType
    library_id = simple.Integer

class ResponseLoadLibrary(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestUnloadLibrary(ClassSerializer):
    auth = AuthType
    library_id = simple.Integer

class ResponseUnloadLibrary(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestRenewApplicationCache(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseRenewApplicationCache(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestGetNodeStatistic(ClassSerializer):
    auth = AuthType

class ResponseGetNodeStatistic(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    class statistic(ClassSerializer):
        loadavg_5 = simple.String
        loadavg_10 = simple.String
        loadavg_15 = simple.String
        utime = simple.String
        stime = simple.String
        swap_outs = simple.String
        maxrss = simple.String
        shared_mem = simple.String
        unshared_stack = simple.String
        unshared_data = simple.String

class RequestStartServerNode(ClassSerializer):
    auth = AuthType

class ResponseStartServerNode(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestRestartServerNode(ClassSerializer):
    auth = AuthType

class ResponseRestartServerNode(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestStopServerNode(ClassSerializer):
    auth = AuthType

class ResponseStopServerNode(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

