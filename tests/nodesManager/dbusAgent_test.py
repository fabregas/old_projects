#!/usr/bin/python

from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

import unittest
import thread
import time
import sys
import dbus
from dbus.types import Dictionary
import gobject
import multiprocessing
from friClientLibrary_test import FRIClient
from blik.nodesManager import friBase

from blik.nodesManager import plugins
from blik.nodesManager.operationsPluginManager import OperationPlugin


class TestPlugin(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        print 'BEFORE CALL START'

        time.sleep(1)

        print self.dbConn
        print self.operationsEngine
        print 'BEFORE CALL END'
        return 0, 'ok'

    def onCallResults(self, operation, status, ret_parameters):
        print 'onCallResults'
        print 'operation: %s'%operation
        print 'status: %s'%status
        print 'params: %s'%ret_parameters

class FakeFailPlugin(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        if parameters.get('error', 'no') == 'yes':
            return 33, 'This is fake error from plugin!'
        return 0,''

    def onCallResults(self, operation, status, ret_parameters):
        pass

plugins.OPERATIONS_PLUGINS['TEST_OPERATION'] = (TestPlugin,FakeFailPlugin)


from blik.nodesManager.dbusAgent import NodesManagerService, NODES_MANAGER_INTERFACE


class DbusAgentTestCase(unittest.TestCase):
    def test_01_test_dbus_iface(self):
        def process_func():
            #init d-bus service
            gobject.threads_init()
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()
            name = dbus.service.BusName(NODES_MANAGER_INTERFACE, bus)
            nodes_manager = NodesManagerService(bus, '/nodes/manager_test')
            loop = gobject.MainLoop()
            loop.run()
            print 'process for D-BUS service started'

        p = multiprocessing.Process(target=process_func, args=())
        p.start()
        print 'process for D-BUS service starting...'

        time.sleep(1)

        try:
            def onSignal(session_id, status, ret_params):
                print 'SIGNAL: ', session_id, status, ret_params

                self.assertEqual(session_id > 0, True)
                self.assertEqual(status > 0, True)
                if status == 1:
                    self.assertEqual(ret_params.has_key('127.0.0.1'), True)

            #init client
            print 'init client'
            bus = dbus.SystemBus()
            proxy = bus.get_object(NODES_MANAGER_INTERFACE, '/nodes/manager_test')
            print proxy.Introspect()
            proxy.connect_to_signal('onOperationFinishEvent', onSignal, dbus_interface=NODES_MANAGER_INTERFACE)

            #negative calls
            session_id, ret_code, ret_message = proxy.callOperationOnCluster('fabregas', 'TEST_CLUSTER', 'TEST_OPERATION', {'error':'yes'})
            self.assertEqual(ret_code, 33, ret_message)
            self.assertEqual(session_id>0, False)

            session_id, ret_code, ret_message = proxy.callOperationOnCluster('e', 'TEST_CLUSTER', 'TEST_OPERATION', Dictionary(signature='ss')) #empty dictionary
            self.assertEqual(ret_code>0, True, ret_message)
            self.assertEqual(session_id>0, False)

            session_id, ret_code, ret_message = proxy.callOperationOnCluster('fabregas', 'fake_cluster', 'TEST_OPERATION', {'e':'4444'})
            self.assertEqual(ret_code>0, True, ret_message)
            self.assertEqual(session_id>0, False)

            session_id, ret_code, ret_message = proxy.callOperationOnCluster('fabregas', 'TEST_CLUSTER', 'fake_operation', {'ddd':'s'})
            self.assertEqual(ret_code>0, True, ret_message)
            self.assertEqual(session_id>0, False)

            #positive tests
            sessions = []
            session_id, ret_code, ret_message = proxy.callOperationOnCluster('fabregas', 'TEST_CLUSTER', 'TEST_OPERATION', {'param1':10})
            self.assertEqual(ret_code, 0, ret_message)
            self.assertEqual(session_id>0, True)
            sessions.append(session_id)

            session_id, ret_code, ret_message = proxy.callOperationOnNodes('fabregas', ['127.0.0.1', '23.23.23.23'], 'TEST_OPERATION', {'param1':10})
            self.assertEqual(ret_code, 0, ret_message)
            self.assertEqual(session_id>0, True)
            sessions.append(session_id)

            client = FRIClient('127.0.0.1', friBase.FRI_BIND_PORT)
            err_code, err_message = client.call({'id':session_id, 'node':'127.0.0.1', 'ret_code':0, 'ret_message':'ok'})
            self.assertEqual(err_code, 0)

            #waiting operations finishing
            for session_id in sessions:
                while True:
                    status_code, status_name = proxy.getOperationStatus(session_id)
                    if status_name == 'INPROGRESS':
                        time.sleep(1)
                        continue
                    break

            time.sleep(1)
        finally:
            print 'process for D-BUS service stoping...'
            p.terminate()
            print 'process for D-BUS service stoped'


    def test_99_stop_dbusAgent(self):
        pass


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################
