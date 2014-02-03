#!/usr/bin/python

import unittest
import socket
import thread
import time
import json
import sys
from blik.nodesManager import friClientLibrary
from blik.utils import friBase

SESSION_ID = 'sfdw12ed2sd2324wedsfsfs'

class FRIServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('0.0.0.0', friBase.FRI_PORT))
        self.sock.listen(2)
        self.stopped = True

    def start(self):
        self.stopped = False

        while not self.stopped:
            (sock, addr) = self.sock.accept()
            if self.stopped:
                sock.close()
                self.sock.close()
                break

            try:
                data = sock.recv(10000)

                json_object = json.loads(data)

                session_id = json_object['id']
                operation = json_object['operation']
                node = json_object['node']
                parameters = json_object['parameters']

                if operation == 'TEST01':
                    if len(parameters) != 2:
                        raise Exception ('Expect 2 parameters')
                    if parameters['param1'] != 'value1' and parameters['param2'] != 'value2':
                        raise Exception ('Parameters values are invalid')

                    ret_code = 0
                    ret_message = 'ok'
                elif operation == 'TEST02':
                    ret_code = 23
                    ret_message = 'fake error'
                else:
                    ret_code = 33
                    ret_message = 'unexpected operation: %s' % operation

            except Exception, err:
                ret_code = 121
                ret_message = str(err)

            try:
                self.send_response(sock, ret_code, ret_message)
            except Exception, err:
                print 'FRI listener: send response error! Details: %s'%err

        print 'SERVER stopped'


    def stop(self):
        self.stopped = True
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        s.connect(('127.0.0.1', friBase.FRI_PORT))
        s.close()

        self.sock.close()
        print 'SOCKET CLOSED'

    def send_response(self, sock, err_code, err_message):
        result = json.dumps({'ret_code':err_code, 'ret_message':err_message})
        sock.send(result)
        sock.close()

class FRIClient:
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.hostname, self.port))
        return sock

    def call(self, data):
        sock = self.connect()

        try:
            sock.send(json.dumps(data))

            resp = sock.recv(1024)
            json_object = json.loads(resp)

            return json_object['ret_code'], json_object['ret_message']
        finally:
            sock.close()


class FriClientLibraryTestCase(unittest.TestCase):
    def test_01_emulate_node(self):
        ret_code, ret_msg = fri_client.operationCall(SESSION_ID, ['127.0.0.1'], 'TEST01', {})
        self.assertEqual(ret_code, 0)

        ret_code, ret_msg = fri_client.operationCall(SESSION_ID, ['127.0.0.1'], 'TEST01', {'param1':'value1', 'param2':'value2'})
        self.assertEqual(ret_code, 0)

        ret_code, ret_msg = fri_client.operationCall(SESSION_ID, ['127.0.0.1', '12.43.22.2'], 'TEST02', {'eeee': 'qqqq'})
        self.assertEqual(ret_code, 0)

        ret_code, ret_msg = fri_client.operationCall(SESSION_ID, ['13.23.3.5', '12.43.22.2'], 'TEST', {})
        self.assertEqual(ret_code, 0)

        time.sleep(4)

    def test_02_emulate_async_resp(self):
        client = FRIClient('127.0.0.1', friBase.FRI_BIND_PORT)
        err_code, err_message = client.call({'id':SESSION_ID, 'node':'test_node01', 'ret_code':0, 'ret_message':'ok', 'progress': '0'})
        self.assertEqual(err_code, 0)
        err_code, err_message = client.call({'id':SESSION_ID, 'node':'test_node01', 'ret_code':0, 'ret_message':'ok', 'progress': '60'})
        self.assertEqual(err_code, 0)
        err_code, err_message = client.call({'id':SESSION_ID, 'node':'test_node01', 'ret_code':0, 'ret_message':'ok', 'progress': '100'})
        self.assertEqual(err_code, 0)

        s = 'qwertyuiop'*1024
        print 'SENDING %s bytes string' %len(s)
        err_code, err_message = client.call({'id':SESSION_ID, 'node':'test_node01', 'ret_code':0, 'ret_message':'ok', 'progress':'100', 'ret_parameters':{'param1':s}})

    def test_99_stop_all(self):
        print 'STOPING fake agent'
        fri.stop()
        print 'STOPING fri client'
        fri_client.stop()
        time.sleep(1)


if __name__ == '__main__':
    ##########################################
    fri_client = friClientLibrary.FriClient()

    def test1(session_id, node, progress, ret_code, ret_message, ret_params_map):
        def assertEqual(a,b):
            if a != b:
                raise Exception ('%s is not equal to %s'%(a,b))

        assertEqual(session_id, SESSION_ID)
        assertEqual(node, 'test_node01')
        assertEqual(ret_code, 0)
        assertEqual(ret_message, 'ok')
        if len(ret_params_map) == 0:
            assertEqual(ret_params_map, {})
        else:
            assertEqual(ret_params_map.keys()[0], 'param1')
        print 'onAsyncOperationResult: node=%s, progress=%s, ret_code=%s'%(node, progress, ret_code)

    fri_client.onAsyncOperationResult = test1
    try:
        fri_client.start()
    except Exception, err:
        print err
        fri_client.stop()
        sys.exit(1)


    fri = FRIServer()
    def server_routine(fri):
        fri.start()

    thread.start_new_thread(server_routine, (fri,))
    time.sleep(0.5)

    ##########################################

    unittest.main()

    ##########################################
