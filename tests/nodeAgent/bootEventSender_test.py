#!/usr/bin/python

import unittest
import thread
import time
import sys
import os
import shutil

import blik.nodeAgent.bootEventSender as BESender
BESender.MANAGEMENT_SERVER = '127.0.0.1'
BESender.SLEEP_SENDER_TIME = 1
BESender.run_command = lambda a: (0,'test','no error')

from blik.nodeAgent.bootEventSender import BootEventSenderThread
BootEventSenderThread._set_new_hostname = lambda a,b: 'test-node'
BootEventSenderThread._remount_devfs = lambda a,b: pass

from blik.utils import friBase
from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

from blik.bootManager.bootEventListener import BootEventListener


class BootEventSenderThreadTestCase(unittest.TestCase):
    def test_simulate_call(self):
        sender = BootEventSenderThread()

        def start_sender(sender):
            ret = sender.run()
            self.assertNotEqual(ret, 0)

        thread.start_new_thread(start_sender,(sender,))

        time.sleep(.1)
        sender.stop()
        time.sleep(1.5)

        try:
            LISTENER = BootEventListener()

            def start_server(node):
                node.start()

            thread.start_new_thread(start_server,(LISTENER,))


            sender = BootEventSenderThread()
            ret = sender.run()

            self.assertEqual(ret, 0)
        finally:
            LISTENER.stop()



if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################


