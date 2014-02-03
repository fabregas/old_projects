from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from WSGI import soapmethod


class NodeManagementApplication ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.NodeManagementApplicationImplementation()
        self.__implementation.start_routine(config)

    def syncronize_application(self, config):
        '''syncronize application cache and configuration'''
        self.__implementation.syncronize_application(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestStartApplication , _returns = ResponseStartApplication(), _outVariableName='responseStartApplication' )
    def StartApplication(self, requestStartApplication):
        return self.__implementation.StartApplication(requestStartApplication)


    @soapmethod( RequestRestartApplication , _returns = ResponseRestartApplication(), _outVariableName='responseRestartApplication' )
    def RestartApplication(self, requestRestartApplication):
        return self.__implementation.RestartApplication(requestRestartApplication)


    @soapmethod( RequestStopApplication , _returns = ResponseStopApplication(), _outVariableName='responseStopApplication' )
    def StopApplication(self, requestStopApplication):
        return self.__implementation.StopApplication(requestStopApplication)


    @soapmethod( RequestLoadLibrary , _returns = ResponseLoadLibrary(), _outVariableName='responseLoadLibrary' )
    def LoadLibrary(self, requestLoadLibrary):
        return self.__implementation.LoadLibrary(requestLoadLibrary)


    @soapmethod( RequestUnloadLibrary , _returns = ResponseUnloadLibrary(), _outVariableName='responseUnloadLibrary' )
    def UnloadLibrary(self, requestUnloadLibrary):
        return self.__implementation.UnloadLibrary(requestUnloadLibrary)


    @soapmethod( RequestRenewApplicationCache , _returns = ResponseRenewApplicationCache(), _outVariableName='responseRenewApplicationCache' )
    def RenewApplicationCache(self, requestRenewApplicationCache):
        return self.__implementation.RenewApplicationCache(requestRenewApplicationCache)


    @soapmethod( RequestGetNodeStatistic , _returns = ResponseGetNodeStatistic(), _outVariableName='responseGetNodeStatistic' )
    def GetNodeStatistic(self, requestGetNodeStatistic):
        return self.__implementation.GetNodeStatistic(requestGetNodeStatistic)


    @soapmethod( RequestStartServerNode , _returns = ResponseStartServerNode(), _outVariableName='responseStartServerNode' )
    def StartServerNode(self, requestStartServerNode):
        return self.__implementation.StartServerNode(requestStartServerNode)


    @soapmethod( RequestRestartServerNode , _returns = ResponseRestartServerNode(), _outVariableName='responseRestartServerNode' )
    def RestartServerNode(self, requestRestartServerNode):
        return self.__implementation.RestartServerNode(requestRestartServerNode)


    @soapmethod( RequestStopServerNode , _returns = ResponseStopServerNode(), _outVariableName='responseStopServerNode' )
    def StopServerNode(self, requestStopServerNode):
        return self.__implementation.StopServerNode(requestStopServerNode)

