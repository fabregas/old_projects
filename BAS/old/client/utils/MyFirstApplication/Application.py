from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from WSGI import soapmethod


class MyFirstApplication ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.MyFirstApplicationImplementation()
        self.__implementation.start_routine(config)

    def syncronize_application(self, config):
        '''syncronize application cache and configuration'''
        self.__implementation.syncronize_application(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestAuthenticate , _returns = ResponseAuthenticate(), _outVariableName='responseAuthenticate' )
    def authenticate(self, requestAuthenticate):
        return self.__implementation.authenticate(requestAuthenticate)


    @soapmethod( RequestEchoMethod , _returns = ResponseEchoMethod(), _outVariableName='responseEchoMethod' )
    def echoMethod(self, requestEchoMethod):
        return self.__implementation.echoMethod(requestEchoMethod)

