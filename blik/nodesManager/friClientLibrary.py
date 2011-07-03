#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.friClientLibrary
@author Konstantin Andrusenko
@date July 2, 2011

This module contains the implementation for the FriClient class.
    FriClient class has following methods:
        - start(...) for starting FRI client as part of nodes manager
        - stop() for stoping FRI client
        - operationCall(...) for calling cluster-wide operation
        - onAsyncOperationResult(...) should be implemented at OperationsEngine
                                      for processing async operation response

"""

import threading
import time
from Queue import Queue
from blik.utils.logger import logger
from blik.nodesManager.friBase import FriServer, FriCaller

STOP_THREAD_EVENT = None

#return codes
RC_OK = 0
RC_ERROR = 1

class FriClient:
    def __init__(self):
        self.__async_threads = []
        self.__listener_thread = None

        self.__async_packets = Queue()


    def start(self, async_threads=3, async_result_threads=5):
        '''
        Start threads for async operations performing and
            start FRI listener for receive async operations results
        '''
        for i in xrange(async_threads):
            thread = AsyncOperationThread(self.__async_packets)
            thread.setName('AsyncOperationThread#%i'%i)
            self.__async_threads.append( thread )

            thread.start()

        self.__listener_thread = FriListenerThread(self.onAsyncOperationResult, workers_count=async_result_threads)
        self.__listener_thread.start()
        while self.__listener_thread.get_state() == FriServer.PENDING_STATE:
            time.sleep(0.1)

        if self.__listener_thread.get_state() != FriServer.STARTED_STATE:
            raise Exception('FriListenerThread is not started!')

    def stop(self):
        '''
        Stop all module threads
        '''
        for thread in self.__async_threads:
            thread.stop()

        self.__listener_thread.stop()

        #waiting threads finishing... 
        #FIXME: may be dead-lock in this block
        self.__listener_thread.join()
        for thread in self.__async_threads:
            thread.join()

    def __form_fri_packet(self, session_id, operation_name, parameters_map):
        if not issubclass(parameters_map.__class__, dict):
            raise Exception('Formating FRI packet error. parameters_map should has dict type')

        packet = {'id': session_id,
                  'operation': operation_name,
                  'parameters': parameters_map}

        return packet

    def operationCall(self, session_id, nodes_list, operation_name, parameters_map):
        '''
        Calling asynchronous operation on nodes list

        @session_id (string) identifier of session (operation instance id)
        @nodes_list (list of string) list of nodes hostnames (or IP addresses)
        @operation_name (string) name of operation
        @parameters_map (dict {<param_name>:<param_value>}) operation parameters

        @return ret_code (integer) code of result
        @return ret_message (string) result description
        '''
        try:
            logger.debug('FriClient: [%s] calling %s operation at nodes %s'%(session_id, operation_name, nodes_list))

            packet = self.__form_fri_packet(session_id, operation_name, parameters_map)

            logger.debug('FriClient: [%s] FRI packet: %s' % (session_id,packet))

            for node in nodes_list:
                packet['node'] = node
                self.__async_packets.put((node, packet))

            return (RC_OK, '')
        except Exception, err:
            err_message = 'FriClient failed on operation call: %s'%err
            logger.error(err_message)

            return (RC_ERROR, err_message)

    def onAsyncOperationResult(self, session_id, node, progress, ret_code, ret_message, ret_params_map):
        '''
        This method should be reimplemented for performing asynchronous operation results

        @session_id (string) identifier of session (operation instance id)
        @node (string) node hostname
        @progress (integer) operation progress in percents (100 for end of operation)
        @ret_code (integer) code of result
        @ret_message (string) result description
        @ret_params_map (dict {<param_name>:<param_value>}) return parameters
        '''
        pass





class AsyncOperationThread(threading.Thread):
    """Thread class for calling asynchronous operation"""
    timeout = 3.0

    def __init__(self, packet_queue):
        self.queue = packet_queue

        # Initialize the thread 
        threading.Thread.__init__(self)

    def stop(self):
        self.queue.put(STOP_THREAD_EVENT)

    def run(self):
        """Thread class run method. Call asynchronous cluster operation"""

        fri_client = FriCaller()

        logger.info('%s started!'%self.getName())
        while True:
            try:
                item = self.queue.get()
                if item == STOP_THREAD_EVENT:
                    logger.info('%s stopped!'%self.getName())
                    break

                #unpack item
                node, packet = item

                err_code, err_message = fri_client.call(node, packet)

                if err_code != RC_OK:
                    logger.error('%s: error while sending %s to node %s. Details: %s' % (self.getName(), packet, node, err_message))
                else:
                    logger.debug('%s: node %s is called successful' % (self.getName(), node))
            except Exception, err:
                err_message = '%s failed: %s'%(self.getName(), err)
                logger.error(err_message)


class ResponsesListenerServer(FriServer):
    def __init__(self, callback_routine, workers_count):
        self.__onAsyncOperationResult = callback_routine

        FriServer.__init__(self, workers_count=workers_count)

    def onAsyncOperationResult( self, json_object ):
            session_id = json_object.get('id', None)
            if session_id is None:
                raise Exception('id element is not found')

            node = json_object.get('node', None)
            if node is None:
                raise Exception('node element is not found')

            progress = json_object.get('progress', None)
            if progress is None:
                raise Exception('progress element is not found')

            try:
                progress = int(progress)
            except:
                raise Exception('Progress parameter must be integer! But: %s'%(progress))

            if progress < 0 or progress > 100:
                raise Exception('Operation progress must be in range 0..100. But: %i'%progress)

            ret_code = json_object.get('ret_code',None)
            if ret_code is None:
                raise Exception('ret_code is not found')

            try:
                ret_code = int(ret_code)
            except:
                raise Exception('Return code parameter must be integer! But: %s'%(ret_code))


            ret_message = json_object.get('ret_message', '')
            ret_params_map = json_object.get('ret_parameters', {})

            if session_id and node:
                self.__onAsyncOperationResult(session_id, node, progress, ret_code, ret_message, ret_params_map)


class FriListenerThread(threading.Thread):
    def __init__(self, callback_thread, workers_count):
        self.server = ResponsesListenerServer(callback_thread, workers_count=workers_count)

        # Initialize the thread 
        threading.Thread.__init__(self, name='FriListenerThread')

    def get_state(self):
        return self.server.state

    def run(self):
        logger.info('FriListenerThread started!')

        self.server.start()

        logger.info('FriListenerThread stopped!')

    def stop(self):
        self.server.stop()


