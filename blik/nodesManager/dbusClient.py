#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.dbusAgent
@author Konstantin Andrusenko
@date August 8, 2011

This module contains the implementation of nodesManager
D-Bus client.
"""

from dbus.types import Dictionary
import dbus, dbus.glib, dbus.service
import gobject

NODES_MANAGER_INTERFACE = 'com.blik.nodesManager'
DBUS_PATH='/nodes/manager'


class DBUSInterfaceClient:
    def __init__(self, skip_resp=False):
        self.skip_resp = skip_resp
        self.bus = dbus.SystemBus()
        self.proxy = self.bus.get_object(NODES_MANAGER_INTERFACE, DBUS_PATH)

        if not skip_resp:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.loop = gobject.MainLoop()
            self.bus.add_signal_receiver(self.__onOperationFinish, dbus_interface = NODES_MANAGER_INTERFACE, signal_name = "onOperationFinishEvent")

    def __onOperationFinish(self,  session_id, status, ret_params):
        try:
            self.onOperationFinish(session_id, status, ret_params)
        finally:
            self.loop.quit()


    def onOperationFinish(self, session_id, status, ret_params):
        """
            This methos sohuld be reimplemented if you can receive operations responses
        """
        pass

    def wait_response(self):
        self.loop.run()


    def call_nodes_operation(self, user_name, nodes_list, operation, op_args):
        """Call callOperationOnNodes operation over DBUS"""

        if not op_args:
            op_args = Dictionary(signature='ss')

        return self.proxy.callOperationOnNodes(user_name, nodes_list, operation, op_args)


    def call_cluster_operation(self, user_name, cluster, operation, op_args):
        """Call callOperationOnCluster operation over DBUS"""

        if not op_args:
            op_args = Dictionary(signature='ss')

        return self.proxy.callOperationOnCluster(user_name, cluster, operation, op_args)


    def get_operation_status(self, session_id):
        """Call getOperationStatus operation over DBUS"""

        return self.proxy.getOperationStatus(session_id)


    def get_log_level(self):
        """Call getLogLevel operation over DBUS"""

        return self.proxy.getLogLevel()

    def set_log_level(self, log_level):
        """Call setLogLevel operation over DBUS"""

        return self.proxy.setLogLevel(log_level)

