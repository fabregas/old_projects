from IOTypesStructure import *
import ApplicationImplementation
import WSGI
import soaplib
from soaplib.util import get_callback_info, get_stacktrace
from soaplib.client import make_service_client
from AsyncWorkManager import AsyncWorkQueue
from WSGI import soapmethod


class FablikManagement ( WSGI.Application ):
    def start(self, config={}):
        ''' init routine for web service'''
        self.__implementation = ApplicationImplementation.FablikManagementImplementation()
        self.__implementation.start_routine(config)

    def synchronize(self, config):
        '''synchronize application cache and configuration'''
        self.__implementation.synchronize(config)

    def stop(self):
        '''destroy routine for web service'''
        self.__implementation.stop_routine()

    @soapmethod( RequestCreateDepartment , _returns = ResponseCreateDepartment(), _outVariableName='responseCreateDepartment' )
    def createDepartment(self, requestCreateDepartment):
        return self.__implementation.createDepartment(requestCreateDepartment)


    @soapmethod( RequestUpdateDepartment , _returns = ResponseUpdateDepartment(), _outVariableName='responseUpdateDepartment' )
    def updateDepartment(self, requestUpdateDepartment):
        return self.__implementation.updateDepartment(requestUpdateDepartment)


    @soapmethod( RequestDeleteDepartment , _returns = ResponseDeleteDepartment(), _outVariableName='responseDeleteDepartment' )
    def deleteDepartment(self, requestDeleteDepartment):
        return self.__implementation.deleteDepartment(requestDeleteDepartment)


    @soapmethod( RequestCreateGroup , _returns = ResponseCreateGroup(), _outVariableName='responseCreateGroup' )
    def createGroup(self, requestCreateGroup):
        return self.__implementation.createGroup(requestCreateGroup)


    @soapmethod( RequestUpdateGroup , _returns = ResponseUpdateGroup(), _outVariableName='responseUpdateGroup' )
    def updateGroup(self, requestUpdateGroup):
        return self.__implementation.updateGroup(requestUpdateGroup)


    @soapmethod( RequestDeleteGroup , _returns = ResponseDeleteGroup(), _outVariableName='responseDeleteGroup' )
    def deleteGroup(self, requestDeleteGroup):
        return self.__implementation.deleteGroup(requestDeleteGroup)


    @soapmethod( RequestCreateUser , _returns = ResponseCreateUser(), _outVariableName='responseCreateUser' )
    def createUser(self, requestCreateUser):
        return self.__implementation.createUser(requestCreateUser)


    @soapmethod( RequestUpdateUser , _returns = ResponseUpdateUser(), _outVariableName='responseUpdateUser' )
    def updateUser(self, requestUpdateUser):
        return self.__implementation.updateUser(requestUpdateUser)


    @soapmethod( RequestDeleteUser , _returns = ResponseDeleteUser(), _outVariableName='responseDeleteUser' )
    def deleteUser(self, requestDeleteUser):
        return self.__implementation.deleteUser(requestDeleteUser)


    @soapmethod( RequestChangeUserPassword , _returns = ResponseChangeUserPassword(), _outVariableName='responseChangeUserPassword' )
    def changeUserPassword(self, requestChangeUserPassword):
        return self.__implementation.changeUserPassword(requestChangeUserPassword)

