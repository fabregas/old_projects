import random
import unittest,time
from suds.client import Client
from datetime import datetime
from thread import start_new_thread

BASE_WSDL = 'http://192.168.80.92:33333/FablikBase/.wsdl'

class Operation:
    def __call__(self):
        raise Exception('Not implemented!')


class AuthOperation (Operation):
    client = Client(BASE_WSDL)

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __call__(self):
        var = self.client.factory.create('RequestAuthenticate')

        var.login = self.username
        var.password = self.password

        result = self.client.service.authenticate(var)

        return result


class LogoutOperation (Operation):
    client = Client(BASE_WSDL)

    def __init__(self, session_id):
        self.session_id = session_id

    def __call__(self):
        var = self.client.factory.create('RequestCloseSession')

        var.session_id = self.session_id

        result = self.client.service.closeSession(var)

        return result



concurent_list = [1,10,100]
operation_list = [AuthOperation('test','test'), LogoutOperation('test')]

class TestClass(unittest.TestCase):
    results = {'Auth':[], 'Logout':[]}

    def __concurent_thread(self):
        count = len(operation_list)

        while not self.stop:
            op_idx = random.randint(0,count-1)

            operation = operation_list[op_idx]

            operation()


    def start_concurents(self, count):
        self.stop = False
        for tick in xrange(count):
            start_new_thread(self.__concurent_thread, ())

    def stop_concurents(self):
        self.stop = True

    def test1_Auth1(self):
        a = AuthOperation('fabregas','blik')

        for concurent in concurent_list:
            self.start_concurents(concurent)

            t0 = datetime.now()
            ret = a()
            dt = datetime.now() - t0

            self.results['Auth'].append( dt )

            self.stop_concurents()

            self.sessionID = ret.session_id
            lo = LogoutOperation(self.sessionID)
            lo()

    def test2_Logout(self):
        li = AuthOperation('fabregas','blik')
        ret = li()
        self.sessionID = ret.session_id
        a = LogoutOperation(self.sessionID)

        for concurent in concurent_list:
            self.start_concurents(concurent)

            t0 = datetime.now()
            ret = a()
            dt = datetime.now() - t0

            self.results['Logout'].append( dt )

            self.stop_concurents()


            li = AuthOperation('fabregas','blik')
            ret = li()
            self.sessionID = ret.session_id
        print self.results

unittest.main()
time.sleep(2)
