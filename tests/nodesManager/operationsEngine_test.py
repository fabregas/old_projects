#!/usr/bin/python

from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

import unittest
import thread
import time
import sys
from friClientLibrary_test import FRIClient
from blik.nodesManager import operationsEngine
from blik.nodesManager import friClientLibrary
from blik.nodesManager import friBase
from blik.utils.databaseConnection import DatabaseConnection


try:
    ENGINE = operationsEngine.OperationsEngine()
except Exception, err:
    print err
    sys.exit(1)


class OperationsEngineTestCase(unittest.TestCase):
    def test_01_call_without_nodes(self):
        def onOperationResultRoutine(operation_name, session_id, status, ret_params_map):
            print '[DEBUG] callback: ', session_id, status, ret_params_map
            self.assertEqual(session_id>0, True)
            self.assertEqual(operation_name, 'TEST_OPERATION')
            self.assertEqual(status, operationsEngine.ORS_TIMEOUTED)
            self.assertEqual(ret_params_map, {})

        sessions = []

        #invalid user name
        session_id, code, message = ENGINE.callOperationOnCluster('fake_user',
                            'TEST_CLUSTER', 'TEST_OPERATION', {'param1':10}, onOperationResultRoutine)
        self.assertEqual(session_id, 0)
        self.assertNotEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #invalid cluster
        session_id, code, message = ENGINE.callOperationOnCluster('fabregas',
                            'fake_cluster', 'TEST_OPERATION', {'param1':10}, onOperationResultRoutine)
        self.assertEqual(session_id, 0)
        self.assertNotEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #invalid operation
        session_id, code, message = ENGINE.callOperationOnCluster('fabregas',
                            'TEST_CLUSTER', 'fake_operation', {'param1':10}, onOperationResultRoutine)
        self.assertEqual(session_id, 0)
        self.assertNotEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #invalid callback routine
        session_id, code, message = ENGINE.callOperationOnCluster('fabregas',
                            'TEST_CLUSTER', 'TEST_OPERATION', {'param1':10}, None)
        sessions.append(session_id)
        self.assertEqual(session_id>0, True)
        self.assertEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #correct parameters
        session_id, code, message = ENGINE.callOperationOnCluster('fabregas',
                            'TEST_CLUSTER', 'TEST_OPERATION', {'param1':10}, onOperationResultRoutine)
        sessions.append(session_id)
        self.assertEqual(session_id>0, True)
        self.assertEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #call on nodes
        session_id, code, message = ENGINE.callOperationOnNodes('fabregas',
                            ['44.134.22.22', '192.168.86.66'], 'TEST_OPERATION', {'param1':10}, onOperationResultRoutine)
        self.assertEqual(session_id, 0)
        self.assertNotEqual(code, 0)

        session_id, code, message = ENGINE.callOperationOnNodes('fabregas',
                            ['127.0.0.1', '192.168.86.66'], 'TEST_OPERATION', {'param1':10}, onOperationResultRoutine)
        sessions.append(session_id)
        self.assertEqual(session_id>0, True)
        self.assertEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        #waiting operations finishing
        for session_id in sessions:
            while True:
                status = ENGINE.getOperationStatus(session_id)
                if status == operationsEngine.ORS_INPROGRESS:
                    time.sleep(1)
                    continue
                break


    def test_03_node_emulation(self):
        def onOperationResultRoutine(operation_name, session_id, status, ret_params_map):
            print '[DEBUG] callback: ', session_id, status, ret_params_map
            self.assertEqual(session_id>0, True)
            self.assertEqual(operation_name, 'TEST_OPERATION')
            self.assertEqual(status, operationsEngine.ORS_COMPLETE)
            self.assertEqual(ret_params_map, {'127.0.0.1':{}})

        def onOperationResultRoutine2(operation_name, session_id, status, ret_params_map):
            print '[DEBUG] callback2: ', session_id, status, ret_params_map
            self.assertEqual(session_id>0, True)
            self.assertEqual(operation_name, 'TEST_OPERATION')
            self.assertEqual(status, operationsEngine.ORS_COMPLETE)
            self.assertEqual(ret_params_map, {'127.0.0.1':{'param1':23}})

        sessions = []

        #call on node
        session_id, code, message = ENGINE.callOperationOnNodes('fabregas',
                            ['127.0.0.1'], 'TEST_OPERATION', {}, onOperationResultRoutine)
        sessions.append(session_id)
        self.assertEqual(session_id>0, True)
        self.assertEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        client = FRIClient('127.0.0.1', friBase.FRI_BIND_PORT)
        err_code, err_message = client.call({'id':session_id, 'node':'127.0.0.1', 'ret_code':0, 'ret_message':'ok'})
        self.assertEqual(err_code, 0)

        session_id, code, message = ENGINE.callOperationOnNodes('fabregas',
                            ['127.0.0.1'], 'TEST_OPERATION', {}, onOperationResultRoutine2)
        sessions.append(session_id)
        self.assertEqual(session_id>0, True)
        self.assertEqual(code, 0)
        self.assertEqual(len(message)>0, True)

        client = FRIClient('127.0.0.1', friBase.FRI_BIND_PORT)
        err_code, err_message = client.call({'id':session_id, 'node':'127.0.0.1', 'ret_code':0, 'ret_message':'ok', 'ret_parameters':{'param1':23}})
        self.assertEqual(err_code, 0)

        #waiting operations finishing
        for session_id in sessions:
            while True:
                status = ENGINE.getOperationStatus(session_id)
                if status == operationsEngine.ORS_INPROGRESS:
                    time.sleep(1)
                    continue
                break

    def test_99_exit(self):
        global ENGINE

        del ENGINE

        #testDB.deleteTestDB()



if __name__ == '__main__':
    ##########################################

    unittest.main()

    ##########################################
