#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodeAgent.friClientLibrary
@author Konstantin Andrusenko
@date July 10, 2011

This module contains the implementation of NodeAgent class.
NodeAgent should be runned in separate thread
(start method block execution)
"""

import threading
from Queue import Queue
from blik.utils.friBase import FriServer
from blik.utils.logger import logger
from blik.nodeAgent.agentPluginsManager import PluginManager
from blik.nodeAgent.bootEventSender import BootEventSenderThread

FINISH_FLAG=None

NODE_AGENT_BIND_PORT=1987

class Operation:
    def __init__(self, session_id, node, operation, parameters):
        self.session_id = session_id
        self.node = node
        self.operation_name = operation
        self.parameters = parameters

class NodeAgent(FriServer):
    def __init__(self, workers_count=3):
        self.__process_threads = []
        self.__operations_queue = Queue()
        self.__boot_event_sender = BootEventSenderThread()
        self.__boot_event_sender.start()

        for i in xrange(workers_count):
            thread = ProcessOperationThread(self.__operations_queue)
            thread.setName('ProcessOperationThread#%i'%i)
            self.__process_threads.append( thread )

            thread.start()

        FriServer.__init__(self, hostname='0.0.0.0', port=NODE_AGENT_BIND_PORT, workers_count=1)

    def onDataReceive( self, json_object ):
        #get session_id
        session_id = json_object.get('id', None)
        if not session_id:
            raise Exception('Element <id> is not found in FRI packet!')

        try:
            session_id = int(session_id)
        except:
            raise Exception('Session is should be integer! But: %s'%session_id)


        #get node
        node = json_object.get('node', None)
        if not node:
            raise Exception('Element <node> is not found in FRI packet!')
        node = node.strip()

        #get operation
        operation = json_object.get('operation', None)
        if not operation:
            raise Exception('Element <operation> is not found in FRI packet')
        operation = operation.strip()

        #get parameters
        parameters = json_object.get('parameters', None)


        #check appropriate plugin
        can_process = PluginManager.can_process_operation( operation )
        if not can_process:
            raise Exception('NodeAgent can not process operation %s. No appropriate plugin found!'%operation)

        op = Operation(session_id, node, operation, parameters)

        self.__operations_queue.put(op)


    def stop(self):
        self.__boot_event_sender.stop()
        FriServer.stop(self)
        for i in self.__process_threads:
            self.__operations_queue.put(FINISH_FLAG)

        self.__operations_queue.join()



class ProcessOperationThread(threading.Thread):
    def __init__(self, queue):
        self.queue = queue

        threading.Thread.__init__(self)

    def run(self):
        name = self.getName()

        logger.info('%s started!'%name)
        while True:
            try:
                operation = self.queue.get()

                if operation == FINISH_FLAG:
                    logger.info('%s stoped!'%name)
                    break

                try:
                    PluginManager.process(operation)
                except Exception, err:
                    logger.error('Processing operation %s failed! Details: %s.\
                                  \nInput parameters: session_id=%s, node=%s, parameters=%s'%
                                    (operation.operation_name, err, operation.session_id,
                                    operation.node, operation.parameters))

            except Exception, err:
                logger.error('%s failed: %s'%(name, err))
            finally:
                self.queue.task_done()

