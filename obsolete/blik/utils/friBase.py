#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.utils.friBase
@author Konstantin Andrusenko
@date July 6, 2011

This module contains the implementation of FriServer and FriCaller class.
    FriCaller class implement call over FRI protocol.
    FriServer class implement basic FRI server.
"""

from Queue import Queue
import threading
import socket
import json
from blik.utils.logger import logger

FRI_PORT = 1987
FRI_BIND_PORT = 1989

#return codes
RC_OK = 0
RC_ERROR = 1

STOP_THREAD_EVENT = None

BUF_SIZE = 1024

class FriServer:
    PENDING_STATE = 'pending'
    STARTED_STATE = 'started'
    FAILED_STATE = 'failed'

    def __init__(self, hostname='0.0.0.0', port=FRI_BIND_PORT, workers_count=2):
        self.hostname = hostname
        self.port = port

        self.queue = Queue()
        self.stopped = True
        self.state = self.PENDING_STATE

        self.__process_async_result_threads = []
        for i in xrange(workers_count):
            thread = ProcessConnectionsThread(self.queue, self.onDataReceive)
            thread.setName('ProcessConnectionsThread#%i'%i)
            self.__process_async_result_threads.append( thread )

            thread.start()

    def onDataReceive( self, json_object ):
        raise Exception('This method should be implemented in child class')

    def __bind_socket(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.sock.bind((self.hostname, self.port))
            self.sock.listen(2)
        except Exception, err:
            self.state = self.FAILED_STATE
            raise err
        else:
            self.state = self.STARTED_STATE
            self.stopped = False

    def start(self):
        self.__bind_socket()

        while not self.stopped:
            try:
                (sock, addr) = self.sock.accept()

                if self.stopped:
                    sock.close()
                    break

                self.queue.put(sock)
            except Exception, err:
                err_message = 'FriServer failed: %s'%err
                logger.error(err_message)


    def stop(self):
        if self.stopped:
            return

        self.stopped = True

        for thread in self.__process_async_result_threads:
            self.queue.put(STOP_THREAD_EVENT)

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1.0)

            if self.hostname == '0.0.0.0':
                hostname = '127.0.0.1'
            else:
                hostname = self.hostname

            s.connect((hostname, self.port))
            s.close()
        except socket.error:
            if s:
                s.close()

        #waiting threads finishing... 
        self.queue.join()

        self.sock.close()



class ProcessConnectionsThread(threading.Thread):
    def __init__(self, queue, event_routine):
        self.queue = queue
        self.__onProcessResult = event_routine

        # Initialize the thread 
        threading.Thread.__init__(self)

    def run(self):
        logger.info('%s started!'%self.getName())
        while True:
            session_id = None
            node = None
            ret_params_map = {}
            ret_code = RC_OK
            ret_message = ''

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

                logger.debug('%s receive: %s'%(self.getName(),data))

                if not data:
                    raise Exception('empty data block')

                json_object = json.loads(data)

                self.__onProcessResult(json_object)
            except Exception, err:
                ret_message = '%s error: %s' % (self.getName(), err)
                ret_code = RC_ERROR
                logger.error(ret_message)
            finally:
                self.queue.task_done()

            try:
                if sock:
                    sock.send(json.dumps({'ret_code':ret_code, 'ret_message':ret_message}))
                    sock.close()
            except Exception, err:
                logger.error('%s sending result error: %s' % (self.getName(), err))


class FriCaller:
    """class for calling asynchronous operation over FRI protocol"""

    def call(self, hostname, packet, port=FRI_PORT, timeout=3.0):
        sock = None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((hostname, port))

            data = json.dumps(packet)

            sock.settimeout(None)

            sock.send(data)

            resp = sock.recv(BUF_SIZE)

            json_object = json.loads(resp)

            return json_object['ret_code'], json_object['ret_message']
        except Exception, err:
            return RC_ERROR, 'FriCaller failed: %s'%err
        finally:
            if sock:
                sock.close()


