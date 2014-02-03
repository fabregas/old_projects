from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
import soaplib.service


class FablikBase ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.FablikBaseImplementation()
        self.__implementation.start_routine(config)

    def syncronize_application(self, config):
        '''syncronize application cache and configuration'''
        self.__implementation.syncronize_application(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soaplib.service.soapmethod( RequestAuthenticate , _returns = ResponseAuthenticate(), _outVariableName='responseAuthenticate' )
    def authenticate(self, requestAuthenticate):
        return self.__implementation.authenticate(requestAuthenticate)


    @soaplib.service.soapmethod( RequestGetMainMenu , _returns = ResponseGetMainMenu(), _outVariableName='responseGetMainMenu' )
    def getMainMenu(self, requestGetMainMenu):
        return self.__implementation.getMainMenu(requestGetMainMenu)


    @soaplib.service.soapmethod( RequestGetInterfaces , _returns = ResponseGetInterfaces(), _outVariableName='responseGetInterfaces' )
    def getInterfaces(self, requestGetInterfaces):
        return self.__implementation.getInterfaces(requestGetInterfaces)


    @soaplib.service.soapmethod( RequestGetDepartaments , _returns = ResponseGetDepartaments(), _outVariableName='responseGetDepartaments' )
    def getDepartaments(self, requestGetDepartaments):
        return self.__implementation.getDepartaments(requestGetDepartaments)


    @soaplib.service.soapmethod( RequestGetPositions , _returns = ResponseGetPositions(), _outVariableName='responseGetPositions' )
    def getPositions(self, requestGetPositions):
        return self.__implementation.getPositions(requestGetPositions)


    @soaplib.service.soapmethod( RequestAppendPosition , _returns = ResponseAppendPosition(), _outVariableName='responseAppendPosition' )
    def appendPosition(self, requestAppendPosition):
        return self.__implementation.appendPosition(requestAppendPosition)


    @soaplib.service.soapmethod( RequestUpdatePosition , _returns = ResponseUpdatePosition(), _outVariableName='responseUpdatePosition' )
    def updatePosition(self, requestUpdatePosition):
        return self.__implementation.updatePosition(requestUpdatePosition)


    @soaplib.service.soapmethod( RequestDeletePosition , _returns = ResponseDeletePosition(), _outVariableName='responseDeletePosition' )
    def deletePosition(self, requestDeletePosition):
        return self.__implementation.deletePosition(requestDeletePosition)


    @soaplib.service.soapmethod( RequestAppendDepartament , _returns = ResponseAppendDepartament(), _outVariableName='responseAppendDepartament' )
    def appendDepartament(self, requestAppendDepartament):
        return self.__implementation.appendDepartament(requestAppendDepartament)


    @soaplib.service.soapmethod( RequestUpdateDepartament , _returns = ResponseUpdateDepartament(), _outVariableName='responseUpdateDepartament' )
    def updateDepartament(self, requestUpdateDepartament):
        return self.__implementation.updateDepartament(requestUpdateDepartament)


    @soaplib.service.soapmethod( RequestDeleteDepartament , _returns = ResponseDeleteDepartament(), _outVariableName='responseDeleteDepartament' )
    def deleteDepartament(self, requestDeleteDepartament):
        return self.__implementation.deleteDepartament(requestDeleteDepartament)

