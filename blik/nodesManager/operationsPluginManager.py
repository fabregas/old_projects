#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.operationsPluginManager
@author Konstantin Andrusenko
@date July 5, 2011

This module contains the implementation for the
OperationsPluginManager class and OperationPlugin interface.
"""

from blik.nodesManager.plugins import OPERATIONS_PLUGINS
from blik.utils.databaseConnection import DatabaseConnection

RC_OK = 0

class OperationPlugin:
    dbConn = None
    operationsEngine = None

    #statuses of operation
    OS_INPROGRESS = 0
    OS_COMPLETED  = 1
    OS_TIMEOUTED  = 2

    def beforeCall(self, operation, call_object, parameters):
        '''
        This hook method call before cluster operation call
        In this method we can append/modify remove operation parameters,
                modify call_object,
                perform database operations (use dbConn),
                perform other cluster operations (use operationsEngine)
        @operation (string) - name of operation for call
        @call_object (CallObject object) - object of calling (cluster, nodes list)
        @parameters (dict {param_name: param_value}) - operation input parameters

        @return (ret_code, ret_message)
        '''
        raise Exception('This method should be implemented in child class')

    def onCallResults(self, operation, status, ret_parameters):
        '''
        This hook method call after cluster operation call
        In this method we can append/modify remove return parameters,
            perform database operations (use dbConn),
            perform other cluster operations (use operationsEngine)
        @operation (string) - name of called operation
        @status (integer) - status of operation
        @ret_parameters (dict {node_hostname : {param_name: param_value}}) -
            return parameters from nodes

        @return None
        '''
        raise Exception('This method should be implemented in child class')

class OperationsPluginManager:
    def __init__(self, operationsEngine):
        dbconn = DatabaseConnection()
        self.operations_map = {}

        for operation, plugins in OPERATIONS_PLUGINS.items():
            plugins_objects = []
            for plugin_class in plugins:
                if not issubclass(plugin_class, OperationPlugin):
                    raise Exception('Plugin class %s is not valid! Plugin should reimplement \
                        OperationPlugin class' % getattr(plugin_class.__name__, '__name__',plugin_class))
                plugin_class.dbConn = dbconn
                plugin_class.operationsEngine = operationsEngine

                plugins_objects.append( plugin_class() )

            self.operations_map[operation] = plugins_objects


    def processBeforeCallPlugins(self, operation, call_object, parameters):
        plugins = self.operations_map.get(operation,[])

        for plugin in plugins:
            ret = plugin.beforeCall(operation, call_object, parameters)
            if not issubclass(ret.__class__, tuple):
                ret_code = 31
                ret_message = 'Method %s.beforeCall should return (ret_code,ret_message), but %s' %(plugin.__class__,ret)
            elif len(ret) != 2:
                ret_code = 32
                ret_message = 'Method %s.beforeCall should return (ret_code,ret_message), but %s'%(plugin.__class__,ret)
            else:
                ret_code, ret_message = ret

            if ret_code != RC_OK:
                return ret_code, ret_message

        return RC_OK, ''

    def processAfterCallPlugins(self, operation, status, ret_parameters):
        plugins = self.operations_map.get(operation,[])

        for plugin in plugins:
            plugin.onCallResults(operation, status, ret_parameters)

