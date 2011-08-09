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
import os
import shutil
import multiprocessing
from friClientLibrary_test import FRIClient
from blik.utils import friBase
from blik.nodesManager import plugins
from blik.nodesManager.dbusAgent import NodesManagerService, NODES_MANAGER_INTERFACE

plugin_src = '''
from blik.nodesManager.operationsPlugin import OperationPlugin
import time

class TestPlugin(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        print 'BEFORE CALL START'

        ops = self.checkRunnedOperations(call_object, ['TEST_OPERATION'])
        if ops:
            raise Exception('TEST_OPERATION is already inprogress in cluster')

        time.sleep(1)

        print self.dbConn
        print self.operationsEngine
        print 'BEFORE CALL END'
        return 0, 'ok'

    def onCallResults(self, operation, session_id, status, ret_parameters):
        print 'onCallResults'
        print 'operation: %s'%operation
        print 'session_id: %s'%session_id
        print 'status: %s'%status
        print 'params: %s'%ret_parameters

class FakeFailPlugin(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        if parameters.get('error', 'no') == 'yes':
            return 33, 'This is fake error from plugin!'
        return 0,''



OPERATIONS_PLUGINS = {'TEST_OPERATION' : (TestPlugin,FakeFailPlugin)}
'''
TEST_PLUGIN_DIR = 'blik/nodesManager/plugins/testPlusgins'

class DbusAgentTestCase(unittest.TestCase):
    def test_01_test_dbus_iface(self):
        def process_func():
            #install test plugin
            os.mkdir(TEST_PLUGIN_DIR)
            open(TEST_PLUGIN_DIR+'/__init__.py','w').write(plugin_src)

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
            proxy.setLogLevel('DEBUG')

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

            #test log level changes
            c_log_level = proxy.getLogLevel()
            self.assertEqual(c_log_level, 'DEBUG')

            proxy.setLogLevel('ERROR')
            c_log_level = proxy.getLogLevel()
            self.assertEqual(c_log_level, 'ERROR')

            try:
                proxy.setLogLevel('FAKE')
            except:
                pass
            else:
                raise Exception('Should be exception in this case!')
            #end test log level changes

            #positive tests
            session_id, ret_code, ret_message = proxy.callOperationOnCluster('fabregas', 'TEST_CLUSTER', 'TEST_OPERATION', {'param1':10})
            self.assertEqual(ret_code, 0, ret_message)
            self.assertEqual(session_id>0, True)

            fail_session_id, ret_code, ret_message = proxy.callOperationOnNodes('fabregas', ['127.0.0.1', '23.23.23.23'], 'TEST_OPERATION',{'a':2})
            self.assertNotEqual(ret_code, 0, ret_message)

            while True:
                status_code, status_name = proxy.getOperationStatus(session_id)
                if status_name == 'INPROGRESS':
                    time.sleep(1)
                    continue
                break

            session_id, ret_code, ret_message = proxy.callOperationOnNodes('fabregas', ['127.0.0.1', '23.23.23.23'], 'TEST_OPERATION', {'param1':10})
            self.assertEqual(ret_code, 0, ret_message)
            self.assertEqual(session_id>0, True)

            client = FRIClient('127.0.0.1', friBase.FRI_BIND_PORT)
            err_code, err_message = client.call({'id':session_id, 'node':'127.0.0.1', 'progress':'100','ret_code':0, 'ret_message':'ok'})
            self.assertEqual(err_code, 0)

            #waiting operations finishing
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


    def test_99_rmtestdir(self):
        print 'REMOVING'
        shutil.rmtree(TEST_PLUGIN_DIR)
        print 'REMOVED'


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################
