#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.dbusAgent
@author Konstantin Andrusenko
@date July 5, 2011

This module contains the implementation of nodesManager
D-Bus service.

This D-Bus service should be called as daemon.
Use INT signal for stoping service
"""

import sys
import dbus, dbus.glib, dbus.service
import gobject
import signal
from blik.nodesManager.operationsPluginManager import OperationsPluginManager
from blik.nodesManager.operationsEngine import OperationsEngine
from blik.utils.logger import logger

NODES_MANAGER_INTERFACE = 'com.blik.nodesManager'

OPER_STATUSES = {0: 'INPROGRESS', 1: 'COMPLETED', 2: 'TIMEOUTED'}

class CallObject:
    CLUSTER = 1
    NODES = 2
    def __init__(self, obj, obj_val):
        self.object = obj
        self.object_value = obj_val


class NodesManagerService(dbus.service.Object):
    def __init__(self, bus, object_path):
        self.operations_engine = OperationsEngine()
        self.pluginManager = OperationsPluginManager(self.operations_engine)

        dbus.service.Object.__init__(self, bus, object_path)

    def stop(self):
        self.operations_engine.stop()

    @dbus.service.signal(dbus_interface=NODES_MANAGER_INTERFACE, signature='isa{sa{ss}}')
    def onOperationFinishEvent(self, session_id, status, ret_params):
        pass

    def __on_operation_results(self, operation_name, session_id, status, ret_params):
        try:
            self.onOperationFinishEvent(session_id, OPER_STATUSES[status], ret_params)

            self.pluginManager.processAfterCallPlugins(operation_name, status, ret_params)
        except Exception, err:
            logger.error('afterCall operation plugins processing error: %s'%err)

    def __call_operation(self, user_name, operation, call_object, parameters):
        if call_object.object == CallObject.CLUSTER:
            return self.operations_engine.callOperationOnCluster(user_name,
                                        call_object.object_value,
                                        operation, parameters,
                                        self.__on_operation_results)
        else:
            #for nodes object
            return self.operations_engine.callOperationOnNodes(user_name,
                                        call_object.object_value,
                                        operation, parameters,
                                        self.__on_operation_results)

    def __cast_parameters(self, parameters):
        ret_params = {}

        for key,value in parameters.items():
            ret_params[str(key)] = str(value)

        return ret_params


    @dbus.service.method(dbus_interface=NODES_MANAGER_INTERFACE,
                    in_signature='sssa{ss}', out_signature='iis')
    def callOperationOnCluster(self, user_name, cluster_name, operation_name, parameters):
        '''
        Call operation in cluster:
            - call all operation's plugins (beforeCall method).
              If some plugin return not zero ret_code then
                return ret_code and ret_message from callOperationOnCluster method
            - call operation over operationsEngine
        '''
        try:
            parameters = self.__cast_parameters(parameters)
            user_name = str(user_name)
            cluster_name = str(cluster_name)
            operation_name = str(operation_name)

            call_object = CallObject(CallObject.CLUSTER, cluster_name)

            ret_code, ret_message = self.pluginManager.processBeforeCallPlugins(operation_name,
                                        call_object, parameters)
            if ret_code:
                return 0, ret_code, ret_message

            return self.__call_operation(user_name, operation_name, call_object, parameters)
        except Exception, err:
            session_id = 0
            ret_code = 21
            ret_message = str(err)
            logger.error(ret_message)

            return session_id, ret_code, ret_message

    @dbus.service.method(dbus_interface=NODES_MANAGER_INTERFACE,
                    in_signature='sassa{ss}', out_signature='iis')
    def callOperationOnNodes(self, user_name, nodes_list, operation_name, parameters):
        '''
        Call operation on nodes list (hostnames):
            - call all operation's plugins (beforeCall method).
              If some plugin return not zero ret_code then
                return ret_code and ret_message from callOperationOnCluster method
            - call operation over operationsEngine
        '''
        try:
            parameters = self.__cast_parameters(parameters)
            user_name = str(user_name)
            operation_name = str(operation_name)
            nodes_list = [str(node) for node in nodes_list]

            call_object = CallObject(CallObject.NODES, nodes_list)

            ret_code, ret_message = self.pluginManager.processBeforeCallPlugins(operation_name,
                                        call_object, parameters)
            if ret_code:
                return 0, ret_code, ret_message

            return self.__call_operation(user_name, operation_name, call_object, parameters)
        except Exception, err:
            session_id = 0
            ret_code = 21
            ret_message = str(err)
            logger.error(ret_message)

            return session_id, ret_code, ret_message

    @dbus.service.method(dbus_interface=NODES_MANAGER_INTERFACE,
                    in_signature='i', out_signature='is')
    def getOperationStatus(self, session_id):
        '''
        Get session status by session_id
        '''
        status_code = self.operations_engine.getOperationStatus(session_id)

        return status_code, OPER_STATUSES[status_code]


if __name__ == '__main__':
    try:
        logger.info('dbusAgent starting...')
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

        loop = gobject.MainLoop()
        bus = dbus.SystemBus()
        name = dbus.service.BusName(NODES_MANAGER_INTERFACE, bus)
        nodes_manager = NodesManagerService(bus, '/nodes/manager')

        def stop(s, p):
            try:
                logger.info('dbusAgent stoping...')

                global nodes_manager
                nodes_manager.stop()
                loop.quit()
            except Exception, err:
                logger.error('Stoping dbusAgent error: %s'%err)

        signal.signal(signal.SIGINT, stop)

        logger.info('dbusAgent started')

        loop.run()

        logger.info('dbusAgent stoped')
    except Exception, err:
        logger.error('dbusAgent error: %s. exit!'%err)
        sys.exit(1)
