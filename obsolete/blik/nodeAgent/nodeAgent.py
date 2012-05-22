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
import dbus
import dbus.service
import dbus.mainloop.glib
from dbus.types import Dictionary

from Queue import Queue
from blik.utils.friBase import FriServer
from blik.utils.logger import logger
from blik.nodeAgent.agentPluginsManager import PluginManager
from blik.nodeAgent.bootEventSender import BootEventSenderThread

FINISH_FLAG=None

NODE_AGENT_BIND_PORT=1987

NODE_AGENT = 'com.blik.nodeAgent'

class NodeAgentEventService (dbus.service.Object):
    @dbus.service.signal(dbus_interface=NODE_AGENT, signature='sssa{ss}')
    def operationReceivedEvent(self, session_id, node, operation, parameters):
        pass

    @dbus.service.signal(dbus_interface=NODE_AGENT, signature='sssa{ss}')
    def operationProcessedEvent(self, session_id, node, operation, parameters):
        pass


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

        #register service on bus
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        #self.loop = gobject.MainLoop()
        bus = dbus.SystemBus()
        name = dbus.service.BusName(NODE_AGENT, bus)
        self.dbus_client = NodeAgentEventService(bus, '/events')

        for i in xrange(workers_count):
            thread = ProcessOperationThread(self.__operations_queue, self.dbus_client)
            thread.setName('ProcessOperationThread#%i'%i)
            self.__process_threads.append( thread )

            thread.start()

        FriServer.__init__(self, hostname='0.0.0.0', port=NODE_AGENT_BIND_PORT, workers_count=1)

    def onDataReceive( self, json_object ):
        #get session_id
        session_id = json_object.get('id', None)
        if session_id is None:
            raise Exception('Element <id> is not found in FRI packet!')

        try:
            session_id = int(session_id)
        except:
            raise Exception('Session is should be integer! But: %s'%session_id)

        if session_id == 0: #LIVE packet
            return


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

        #send message to D-BUS
        op_args = Dictionary(signature='ss')
        op_args.update(parameters)
        self.dbus_client.operationReceivedEvent(str(session_id), str(node), str(operation), op_args)

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
    def __init__(self, queue, dbus_client):
        self.queue = queue
        self.dbus_client = dbus_client

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

                op_args = Dictionary(signature='ss')
                op_args.update(operation.parameters)
                self.dbus_client.operationProcessedEvent(str(operation.session_id), str(operation.node), 
                                    str(operation.operation_name), op_args)
            except Exception, err:
                logger.error('%s failed: %s'%(name, err))
            finally:
                self.queue.task_done()



