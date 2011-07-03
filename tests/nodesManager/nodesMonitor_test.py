#!/usr/bin/python

from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'
Config.nodes_monitor_timeout = 1
Config.monitor_wait_response_timeout = 1

import unittest
import thread
import time
import sys
from blik.nodesManager import friBase
from blik.nodesManager.nodesMonitor import NodesMonitor
from blik.utils.databaseConnection import DatabaseConnection

MONITOR = None

class NodeSimulator(friBase.FriServer):
    def __init__(self):
        friBase.FriServer.__init__(self, port=friBase.FRI_PORT, workers_count=1)

    def onAsyncOperationResult( self, json_object ):
        print 'NODE RECEIVED: ', json_object
        session_id = json_object.get('id')
        if int(session_id) != 0:
            raise Exception('id=0 expected!!!')

        node = json_object.get('node')
        if node != '':
            raise Exception('empty node field expected!!!')

        operation = json_object.get('operation')
        if operation != 'LIVE':
            raise Exception('LIVE operation expected!!!')



class NodesMonitorTestCase(unittest.TestCase):
    def test_01_init_monitor(self):
        global MONITOR

        MONITOR = NodesMonitor()
        MONITOR.start()

    def test_99_stop_monitor(self):
        global MONITOR
        if MONITOR:
            MONITOR.stop()
            time.sleep(1)

    def test_02_simulate_node(self):
        db = DatabaseConnection()
        state = db.select("SELECT current_state FROM nm_node WHERE hostname='127.0.0.1'")[0][0]
        self.assertEqual(state, 0)#OFF


        node = NodeSimulator()
        def start_server(node):
            node.start()

        thread.start_new_thread(start_server,(node,))

        try:
            time.sleep(1.5)
            state = db.select("SELECT current_state FROM nm_node WHERE hostname='127.0.0.1'")[0][0]
            self.assertEqual(state, 1)#ON
            node.stop()

            time.sleep(1.5)

            state = db.select("SELECT current_state FROM nm_node WHERE hostname='127.0.0.1'")[0][0]
            self.assertEqual(state, 0)#OFF
        finally:
            node.stop()


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################

