#!/usr/bin/python

import unittest
import thread
import time
import sys
import os
import shutil

from blik.nodeAgent.agentPluginsManager import NodeAgentPlugin, PluginManager

#------------------------------------------------------
plugin = '''
from blik.nodeAgent.agentPluginsManager import NodeAgentPlugin

class TestPlugin(NodeAgentPlugin):
    def process(self, parameters):
        print 'PLUGIN #2: %s'%parameters

        self.updateOperationProgress(100, ret_message='all steps are processed by PLUGIN #2!')

        print 'PLUGIN #2 PROCESSED'
'''
TEST_PLUGIN_DIR = 'blik/nodeAgent/plugins/testPlusginsGroup'
os.mkdir(TEST_PLUGIN_DIR)
open(TEST_PLUGIN_DIR+'/__init__.py','w').write("from plugin2 import TestPlugin\nOPERATIONS_PLUGINS={'TEST_OPERATION2': TestPlugin}")
open(TEST_PLUGIN_DIR+'/plugin2.py','w').write(plugin)


#------------------------------------------------------

class TestPlugin(NodeAgentPlugin):
    def process(self, parameters):
        print 'STARTING: %s'%parameters

        try:
            self.updateOperationProgress(5, ret_message='started processing...')
            time.sleep(.2)
            self.updateOperationProgress(30, ret_message='step2 processed!')
            time.sleep(.3)
            self.updateOperationProgress(80, ret_message='step3 processed!')

            ret = parameters['test1']
            time.sleep(.1)
            self.updateOperationProgress(100, ret_message='all steps are processed!')
        except Exception, err:
            self.updateOperationProgress(88, ret_message='Error: %s'%err, ret_code=324)

        print 'PROCESSED'

from blik.nodeAgent import plugins
plugins.OPERATIONS_PLUGINS['TEST_OPERATION'] = TestPlugin
PluginManager.init()

from blik.utils import friBase
from blik.nodeAgent.nodeAgent import NodeAgent

class FarnsworthSimulator(friBase.FriServer):
    def __init__(self):
        friBase.FriServer.__init__(self, workers_count=1)

    def onDataReceive( self, json_object ):
        print 'FARNSWOTH RECEIVED: ', json_object
        def check_key(key):
            if not json_object.has_key(key):
                print 'ERROR: element <%s> is not found!'%key

        check_key('id')
        check_key('node')
        check_key('ret_parameters')
        check_key('ret_code')
        check_key('ret_message')
        check_key('progress')


AGENT = None

class NodeAgentTestCase(unittest.TestCase):
    def test_01_init_agent(self):
        global AGENT

        AGENT = NodeAgent()

        def start_server(node):
            node.start()

        thread.start_new_thread(start_server,(AGENT,))

        time.sleep(1)

    def test_99_stop_agent(self):
        global AGENT
        if AGENT:
            AGENT.stop()
            time.sleep(1)

    def test_02_simulate_call(self):
        farnsworth = FarnsworthSimulator()
        def start_server(node):
            node.start()


        thread.start_new_thread(start_server,(farnsworth,))
        time.sleep(.5)

        try:
            caller = friBase.FriCaller()
            packet = {  'id': 23532453,
                        'node': '127.0.0.1',
                        'operation': 'TEST_OPERATION',
                        'parameters': {'test1':'value222'}}

            code,msg = caller.call('127.0.0.1', packet, 1987)

            self.assertEqual(code, 0, msg)

            packet['id'] = 666
            packet['parameters'] = {}
            code,msg = caller.call('127.0.0.1', packet, 1987)
            self.assertEqual(code, 0, msg)

            #plugin 2 operation
            packet['operation'] = 'TEST_OPERATION2'
            code,msg = caller.call('127.0.0.1', packet, 1987)
            self.assertEqual(code, 0, msg)

            #fake operation
            packet['operation'] = 'FAKE_OPERATION'
            code,msg = caller.call('127.0.0.1', packet, 1987)
            self.assertNotEqual(code, 0)


            time.sleep(1)
        finally:
            farnsworth.stop()


    def test_03_rmtestdir(self):
        print 'REMOVING'
        shutil.rmtree(TEST_PLUGIN_DIR)
        print 'REMOVed'

if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################


