#!/usr/bin/python

import unittest
import thread
import time
import sys

from blik.nodeAgent.agentPluginsManager import NodeAgentPlugin, PluginManager

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

            #fake operation
            packet['operation'] = 'FAKE_OPERATION'
            code,msg = caller.call('127.0.0.1', packet, 1987)
            self.assertNotEqual(code, 0)


            time.sleep(1)
        finally:
            farnsworth.stop()


    '''
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
        print 'STOPED'
    '''


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################


