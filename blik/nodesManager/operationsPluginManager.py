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

import os
from blik.nodesManager import plugins
from blik.utils.databaseConnection import DatabaseConnection
from blik.utils.logger import logger
from operationsPlugin import OperationPlugin


RC_OK = 0


class OperationsPluginManager:
    def __init__(self, operationsEngine):
        dbconn = DatabaseConnection()
        self.operations_map = {}

        OPERATIONS_PLUGINS = self._import_plugins()
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

    def _import_plugins(self):
        work_dir = plugins.__path__[0]
        dirs = os.listdir(work_dir)

        ret_map = plugins.OPERATIONS_PLUGINS
        for item in dirs:
            item_path = os.path.join(work_dir, item)

            if not os.path.isdir(item_path):
                continue

            try:
                exec('from blik.nodesManager.plugins.%s import OPERATIONS_PLUGINS'%item)

                ret_map.update(OPERATIONS_PLUGINS)
            except Exception, err:
                logger.warning('Can not import %s module. Details: %s'%(item_path,err))

        return ret_map


    def processBeforeCallPlugins(self, operation, call_object, parameters):
        plugins = self.operations_map.get(operation,[])

        for plugin in plugins:
            try:
                ret = plugin.beforeCall(operation, call_object, parameters)

                if issubclass(ret.__class__, tuple) and (len(ret) != 2):
                    ret_code, ret_message = ret
                else:
                    ret_code, ret_message = RC_OK, 'ok'

                if ret_code != RC_OK:
                    return ret_code, ret_message
            except Exception, err:
                return 13, 'Processing plugin %s failed. Details: %s'%(plugin.__class__.__name__, err)

        return RC_OK, ''

    def processAfterCallPlugins(self, operation, session_id, status, ret_parameters):
        plugins = self.operations_map.get(operation,[])

        for plugin in plugins:
            plugin.onCallResults(operation, session_id, status, ret_parameters)

