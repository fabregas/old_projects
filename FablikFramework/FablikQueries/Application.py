from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from soaplib.util import get_callback_info, get_stacktrace
from soaplib.client import make_service_client
from AsyncWorkManager import AsyncWorkQueue
from WSGI import soapmethod


class FablikQueries ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.FablikQueriesImplementation()
        self.__implementation.start_routine(config)

    def synchronize(self, config):
        '''synchronize application cache and configuration'''
        self.__implementation.synchronize(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestExecuteQuery , _returns = ResponseExecuteQuery(), _outVariableName='responseExecuteQuery' )
    def executeQuery(self, requestExecuteQuery):
        return self.__implementation.executeQuery(requestExecuteQuery)


    @soapmethod( RequestCreateCursor , _returns = ResponseCreateCursor(), _outVariableName='responseCreateCursor' )
    def createCursor(self, requestCreateCursor):
        return self.__implementation.createCursor(requestCreateCursor)


    @soapmethod( RequestCloseCursor , _returns = ResponseCloseCursor(), _outVariableName='responseCloseCursor' )
    def closeCursor(self, requestCloseCursor):
        return self.__implementation.closeCursor(requestCloseCursor)


    @soapmethod( RequestGetCursorData , _returns = ResponseGetCursorData(), _outVariableName='responseGetCursorData' )
    def getCursorData(self, requestGetCursorData):
        return self.__implementation.getCursorData(requestGetCursorData)

