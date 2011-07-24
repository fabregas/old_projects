#!/usr/bin/python

import unittest
import thread
import time
import sys
import os
import shutil

from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

from blik.bootManager.bootEventListener import BootEventListener
from blik.utils.databaseConnection import DatabaseConnection
from blik.utils import friBase

LISTENER = None

class BootEventListenerTestCase(unittest.TestCase):
    def test_01_init_listener(self):
        global LISTENER

        LISTENER = BootEventListener()

        def start_server(node):
            node.start()

        thread.start_new_thread(start_server,(LISTENER,))

        time.sleep(1)

    def test_99_stop_agent(self):
        global LISTENER
        if LISTENER:
            LISTENER.stop()
            time.sleep(1)

    def test_02_simulate_call(self):
        dbconn = DatabaseConnection()
        caller = friBase.FriCaller()
        packet = {  'uuid': '32542523esdf23r32r3fr',
                    'hostname': 'test_node_01',
                    'ip_address': '193.13.12.22',
                    'mac_address': '34:34:34:34:34:34',
                    'login': 'fabregas',
                    'password': 'test_pwd',
                    'processor': 'Intel i7 3.4Ghz',
                    'memory': '4023'
                    }

        code,msg = caller.call('127.0.0.1', packet, 1986)
        self.assertEqual(code, 0, msg)

        rows = dbconn.select("SELECT hostname FROM nm_node WHERE node_uuid='32542523esdf23r32r3fr'")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 'test_node_01')

        #change params and call
        packet['hostname'] = 'node_01'
        code,msg = caller.call('127.0.0.1', packet, 1986)
        self.assertEqual(code, 0, msg)
        rows = dbconn.select("SELECT hostname, login FROM nm_node WHERE node_uuid='32542523esdf23r32r3fr'")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][0], 'node_01')
        self.assertEqual(rows[0][1], 'fabregas')

        #ip_address is optional
        del packet['ip_address']
        code,msg = caller.call('127.0.0.1', packet, 1986)
        self.assertEqual(code, 0, msg)

        #ip_address is optional
        del packet['login']
        code,msg = caller.call('127.0.0.1', packet, 1986)
        self.assertNotEqual(code, 0, msg)

    def test_03_load(self):
        packet = {  'uuid': '2r3fr',
                    'hostname': 'test_node_01',
                    'ip_address': '193.13.12.22',
                    'mac_address': '34:34:34:34:34:34',
                    'login': 'fabregas',
                    'password': 'test_pwd',
                    'processor': 'Intel i7 3.4Ghz',
                    'memory': '4023'
                    }

        def call_100(packet):
            caller = friBase.FriCaller()
            for i in xrange(50):
                packet['uuid'] = 'uuid_' + str(i)
                packet['hostname'] = 'node_' + str(i)

                code,msg = caller.call('127.0.0.1', packet, 1986)
                self.assertEqual(code, 0, msg)


        for i in xrange(10):
            thread.start_new_thread(call_100,(packet,))

        time.sleep(2)


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################


