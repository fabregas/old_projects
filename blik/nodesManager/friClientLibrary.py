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

import json
import threading
import socket
import time
from Queue import Queue
from blik.utils.logger import logger

FRI_PORT = 1987
FRI_BIND_PORT = 1989

#return codes
RC_OK = 0
RC_ERROR = 1

STOP_THREAD_EVENT = None

BUF_SIZE = 1024

class FriClient:
    def __init__(self):
        self.__async_threads = []
        self.__process_async_result_threads = []
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

        result_sockets = Queue()
        for i in xrange(async_result_threads):
            thread = ProcessAsyncResultThread(result_sockets, self.onAsyncOperationResult)
            thread.setName('ProcessAsyncResultThread#%i'%i)
            self.__process_async_result_threads.append( thread )

            thread.start()

        self.__listener_thread = FriListenerThread(result_sockets)
        self.__listener_thread.start()
        while self.__listener_thread.status == 'pending':
            time.sleep(0.1)

        if self.__listener_thread.stopped:
            raise Exception('FriListenerThread is not started!')

    def stop(self):
        '''
        Stop all module threads
        '''
        for thread in self.__async_threads:
            thread.stop()

        for thread in self.__process_async_result_threads:
            thread.stop()

        self.__listener_thread.stop()

        #waiting threads finishing... 
        #FIXME: may be dead-lock in this block
        self.__listener_thread.join()
        for thread in self.__async_threads:
            thread.join()
        for thread in self.__process_async_result_threads:
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

    def onAsyncOperationResult(self, session_id, node, ret_code, ret_message, ret_params_map):
        '''
        This method should be reimplemented for performing asynchronous operation results

        @session_id (string) identifier of session (operation instance id)
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

    def __fri_call(self, hostname, packet):
        sock = None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((hostname, FRI_PORT))

            data = json.dumps(packet)

            sock.settimeout(None)

            sock.send(data)

            resp = sock.recv(BUF_SIZE)

            json_object = json.loads(resp)

            return json_object['ret_code'], json_object['ret_message']
        except Exception, err:
            return RC_ERROR, str(err)
        finally:
            if sock:
                sock.close()

    def stop(self):
        self.queue.put(STOP_THREAD_EVENT)

    def run(self):
        """Thread class run method. Call asynchronous cluster operation"""

        logger.info('%s started!'%self.getName())
        while True:
            try:
                item = self.queue.get()
                if item == STOP_THREAD_EVENT:
                    logger.info('%s stopped!'%self.getName())
                    break

                #unpack item
                node, packet = item

                err_code, err_message = self.__fri_call(node, packet)

                if err_code != RC_OK:
                    logger.error('%s: error while sending %s to node %s. Details: %s' % (self.getName(), packet, node, err_message))
                else:
                    logger.debug('%s: node %s is called successful' % (self.getName(), node))
            except Exception, err:
                err_message = '%s failed: %s'%(self.getName(), err)
                logger.error(err_message)



class FriListenerThread(threading.Thread):
    def __init__(self, queue):
        self.queue = queue
        self.status = 'pending'
        self.stopped = True

        # Initialize the thread 
        threading.Thread.__init__(self, name='FriListenerThread')

    def __bind_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.bind(('0.0.0.0', FRI_BIND_PORT))
            self.sock.listen(1)
            self.stopped = False
        finally:
            self.status = 'complete'

    def run(self):
        self.status = 'pending'
        self.__bind_socket()

        logger.info('FriListenerThread started!')

        while not self.stopped:
            try:
                (sock, addr) = self.sock.accept()

                if self.stopped:
                    sock.close()
                    break

                self.queue.put(sock)
            except Exception, err:
                err_message = 'FriListenerThread failed: %s'%err
                logger.error(err_message)

        logger.info('FriListenerThread stopped!')

    def stop(self):
        self.stopped = True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(('127.0.0.1', FRI_BIND_PORT))
            s.close()
        except socket.error:
            if s:
                s.close()

        self.sock.close()


class ProcessAsyncResultThread(threading.Thread):
    def __init__(self, queue, event_routine):
        self.queue = queue
        self.__onAsyncOperationResult = event_routine

        # Initialize the thread 
        threading.Thread.__init__(self)

    def stop(self):
        self.queue.put(STOP_THREAD_EVENT)

    def run(self):
        logger.info('%s started!'%self.getName())
        while True:
            session_id = None
            node = None
            ret_params_map = {}

            try:
                sock = self.queue.get()

                if sock == STOP_THREAD_EVENT:
                    logger.info('%s stopped!'%self.getName())
                    break

                data = ''
                while True:
                    received = sock.recv(BUF_SIZE)
                    if not received:
                        break

                    data += received

                    if len(received) < BUF_SIZE:
                        break

                logger.debug('%s receive:\n%s'%(self.getName(),data))

                if not data:
                    raise Exception('empty data block')

                json_object = json.loads(data)

                session_id = json_object.get('id', None)
                if session_id is None:
                    raise Exception('id element is not found')

                node = json_object.get('node', None)
                if node is None:
                    raise Exception('node element is not found')

                ret_code = json_object.get('ret_code',None)
                if ret_code is None:
                    raise Exception('ret_code is not found')

                ret_message = json_object.get('ret_message', '')
                ret_params_map = json_object.get('ret_parameters', {})
            except Exception, err:
                ret_message = '%s error: %s' % (self.getName(), err)
                ret_code = RC_ERROR
                logger.error(ret_message)


            try:
                if session_id and node:
                    self.__onAsyncOperationResult(session_id, node, ret_code, ret_message, ret_params_map)
            except Exception, err:
                logger.error('onAsyncOperationResult error: %s' % err)


            try:
                if sock:
                    sock.send(json.dumps({'ret_code':ret_code, 'ret_message':ret_message}))
                    sock.close()
            except Exception, err:
                log.error('%s sending result error: %s' % (self.getName(), err))

