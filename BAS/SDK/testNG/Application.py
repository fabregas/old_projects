from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from soaplib.util import get_callback_info, get_stacktrace
from soaplib.client import make_service_client
from AsyncWorkManager import AsyncWorkQueue
from WSGI import soapmethod


class testNG ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.testNGImplementation()
        self.__implementation.start_routine(config)

    def syncronize_application(self, config):
        '''syncronize application cache and configuration'''
        self.__implementation.syncronize_application(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestRunNGMethod , _returns = ResponseRunNGMethod(), _outVariableName='responseRunNGMethod' )
    def runNGMethod(self, requestRunNGMethod):
        return self.__implementation.runNGMethod(requestRunNGMethod)

