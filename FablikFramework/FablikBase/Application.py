from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from soaplib.util import get_callback_info, get_stacktrace
from soaplib.client import make_service_client
from AsyncWorkManager import AsyncWorkQueue
from WSGI import soapmethod


class FablikBase ( WSGI.SoapApplication ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.FablikBaseImplementation()
        self.__implementation.start_routine(config)

    def synchronize(self, config):
        '''synchronize application cache and configuration'''
        self.__implementation.synchronize(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestAuthenticate , _returns = ResponseAuthenticate(), _outVariableName='responseAuthenticate' )
    def authenticate(self, requestAuthenticate):
        return self.__implementation.authenticate(requestAuthenticate)


    @soapmethod( RequestAuthorize , _returns = ResponseAuthorize(), _outVariableName='responseAuthorize' )
    def authorize(self, requestAuthorize):
        return self.__implementation.authorize(requestAuthorize)


    @soapmethod( RequestCloseSession , _returns = ResponseCloseSession(), _outVariableName='responseCloseSession' )
    def closeSession(self, requestCloseSession):
        return self.__implementation.closeSession(requestCloseSession)


    @soapmethod( RequestGetMainMenu , _returns = ResponseGetMainMenu(), _outVariableName='responseGetMainMenu' )
    def getMainMenu(self, requestGetMainMenu):
        return self.__implementation.getMainMenu(requestGetMainMenu)


    @soapmethod( RequestGetInterfaces , _returns = ResponseGetInterfaces(), _outVariableName='responseGetInterfaces' )
    def getInterfaces(self, requestGetInterfaces):
        return self.__implementation.getInterfaces(requestGetInterfaces)


    @soapmethod( RequestGetForm , _returns = ResponseGetForm(), _outVariableName='responseGetForm' )
    def getForm(self, requestGetForm):
        return self.__implementation.getForm(requestGetForm)

