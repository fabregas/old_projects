from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from WSGI import soapmethod


class SystemApplication ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.SystemApplicationImplementation()
        self.__implementation.start_routine(config)

    def syncronize_application(self, config):
        '''syncronize application cache and configuration'''
        self.__implementation.syncronize_application(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestDeployApplication , _returns = ResponseDeployApplication(), _outVariableName='responseDeployApplication' )
    def DeployApplication(self, requestDeployApplication):
        return self.__implementation.DeployApplication(requestDeployApplication)


    @soapmethod( RequestUndeployApplication , _returns = ResponseUndeployApplication(), _outVariableName='responseUndeployApplication' )
    def UndeployApplication(self, requestUndeployApplication):
        return self.__implementation.UndeployApplication(requestUndeployApplication)


    @soapmethod( RequestStartApplication , _returns = ResponseStartApplication(), _outVariableName='responseStartApplication' )
    def StartApplication(self, requestStartApplication):
        return self.__implementation.StartApplication(requestStartApplication)


    @soapmethod( RequestRestartApplication , _returns = ResponseRestartApplication(), _outVariableName='responseRestartApplication' )
    def RestartApplication(self, requestRestartApplication):
        return self.__implementation.RestartApplication(requestRestartApplication)

    @soapmethod( RequestActivateApplication , _returns = ResponseActivateApplication(), _outVariableName='responseActivateApplication' )
    def ActivateApplication(self, requestActivateApplication):
        return self.__implementation.ActivateApplication(requestActivateApplication)

    @soapmethod( RequestStopApplication , _returns = ResponseStopApplication(), _outVariableName='responseStopApplication' )
    def StopApplication(self, requestStopApplication):
        return self.__implementation.StopApplication(requestStopApplication)


    @soapmethod( RequestRenewApplicationCache , _returns = ResponseRenewApplicationCache(), _outVariableName='responseRenewApplicationCache' )
    def RenewApplicationCache(self, requestRenewApplicationCache):
        return self.__implementation.RenewApplicationCache(requestRenewApplicationCache)

    @soapmethod( RequestGetApplicationState , _returns = ResponseGetApplicationState(), _outVariableName='responseGetApplicationState' )
    def GetApplicationState(self, requestGetApplicationState):
        return self.__implementation.GetApplicationState(requestGetApplicationState)
