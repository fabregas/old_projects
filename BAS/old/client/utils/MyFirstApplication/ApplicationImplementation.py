from IOTypesStructure import *

class MyFirstApplicationImplementation:
    def start_routine(self, config):
        pass

    def syncronize_application(self, config):
        pass

    def stop_routine(self):
        pass

    def authenticate(self, request):
        code,message = (0, 'user is authenticated')

        if (request.user_name != 'test_user') or (request.user_password != 'test_password'):
            code,message = (-1,'authentication failed!!!')

        return ResponseAuthenticate(ret_code=code, ret_message=message)

    def echoMethod(self, request):
        return ResponseEchoMethod(ret_message = request.message)

