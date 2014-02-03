import soaplib
from soaplib.serializers.clazz import ClassSerializer
import soaplib.serializers.primitive as simple
import soaplib.serializers.binary as binary

class AuthType(ClassSerializer):
    login = simple.String
    password = simple.String

class RequestDeployApplication(ClassSerializer):
    auth = AuthType
    source = binary.Attachment
    app_name = simple.String
    app_version = simple.String
    app_type = simple.String

class ResponseDeployApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    application_id = simple.Integer

class RequestUndeployApplication(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseUndeployApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

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

class RequestRenewApplicationCache(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseRenewApplicationCache(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

class RequestGetApplicationState(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseGetApplicationState(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String
    state = simple.String

class RequestActivateApplication(ClassSerializer):
    auth = AuthType
    application_id = simple.Integer

class ResponseActivateApplication(ClassSerializer):
    ret_code = simple.Integer
    ret_message = simple.String

