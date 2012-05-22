#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodeAgent.agentPluginsManager
@author Konstantin Andrusenko
@date July 10, 2011

This module contains the implementation of NodeAgentPlugin classes.
"""

import os
from blik.nodeAgent import plugins
from blik.utils.logger import logger
from agentPlugin import NodeAgentPlugin

class PluginManager:
    operations_map = {}

    @staticmethod
    def _import_plugins():
        work_dir = plugins.__path__[0]
        dirs = os.listdir(work_dir)

        ret_map = plugins.OPERATIONS_PLUGINS
        for item in dirs:
            item_path = os.path.join(work_dir, item)

            if not os.path.isdir(item_path):
                continue

            try:
                exec('from blik.nodeAgent.plugins.%s import OPERATIONS_PLUGINS'%item)

                ret_map.update(OPERATIONS_PLUGINS)
            except ImportError, err:
                logger.warning('Can not import %s module. Details: %s'%(item_path,err))

        return ret_map

    @staticmethod
    def init():
        OPERATIONS_PLUGINS = PluginManager._import_plugins()

        for operation, plugin_class in OPERATIONS_PLUGINS.items():
            plugins_objects = []

            if not issubclass(plugin_class, NodeAgentPlugin):
                raise Exception('Plugin class %s is not valid! Plugin should reimplement \
                    NodeAgentPlugin class' % getattr(plugin_class.__name__, '__name__',plugin_class))

            PluginManager.operations_map[operation] = plugin_class

    @staticmethod
    def can_process_operation(operation_name):
        if PluginManager.operations_map.has_key(operation_name):
            return True

        return False

    @staticmethod
    def process(operation_obj):
        try:
            processor = PluginManager.operations_map.get(operation_obj.operation_name, None)

            if not processor:
                raise Exception('Processor is not found for %s operation'%operation_obj.operation_name)

            proc = processor(operation_obj.session_id, operation_obj.node)
            proc.process(operation_obj.parameters)
        except Exception, err:
            logger.error('Processing operation %s failed! Details: %s.\
                            \nInput parameters: session_id=%s, node=%s, parameters=%s'%
                                (operation_obj.operation_name, err, operation_obj.session_id,
                                operation_obj.node, operation_obj.parameters))




########################################


PluginManager.init()
