import unittest, base64
from ApplicationImplementation import *
import IOTypesStructure as types
from datetime import datetime


import Database
#---------------------------------------
class Config:
    def __init__(self):
        self.cluster_id = 1

class ApplicationServer:
    def __init__(self):
        self.database = Database.Database('host=%s user=%s dbname=%s'%(DB_HOST, DB_USER, DB_NAME))
        self.config = Config()

    def start_application_in_cluster(self, app_id):
        print 'start application in cluster', app_id

    def stop_application_in_cluster(self, app_id):
        print 'stop application in cluster', app_id

    def start_application(self, app_id):
        print 'start application',app_id
        return (0,'ok')

    def stop_application(self, app_id):
        print 'stop application',app_id
        return (0,'ok')

    def renew_application_cache(self, app_id):
        print 'renew application cache',app_id
        return (0,'ok')

    def start(self):
        print 'start server'

    def stop(self):
        print 'stop server'

class AppWraper:
    def __init__(self, data):
        self.data = data
#---------------------------------------


DB_HOST = '127.0.0.1'
DB_USER = 'postgres'
DB_NAME = 'bas_db'

server = ApplicationServer()
APP = NodeManagementApplicationImplementation()
APP.start_routine({'server':server})

AUTH = types.AuthType(login='fabregas', password='blik')

APP_ID = 85


class TestNodeManagementApplication(unittest.TestCase):
    def test2_StartApplication(self):
        request = types.RequestStartApplication(auth=AUTH, application_id=APP_ID)
        
        response = APP.StartApplication(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

    
    def test3_RestartApplication(self):
        request = types.RequestRestartApplication(auth=AUTH, application_id=APP_ID)

        response = APP.RestartApplication(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)
    

    def test4_RenewApplicationCache(self):
        request = types.RequestRenewApplicationCache(auth=AUTH, application_id=APP_ID)

        response = APP.RenewApplicationCache(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

    def test5_StopApplication(self):
        request = types.RequestStopApplication(auth=AUTH, application_id=APP_ID)

        response = APP.StopApplication(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

    
    def test7_GetNodeStatistic(self):
        request = types.RequestGetNodeStatistic(auth=AUTH)
        response = APP.GetNodeStatistic(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)


    def test8_StartServerNode(self):
        #write code for testing StartServerNode routine

        pass

    def test9_RestartServerNode(self):
        #write code for testing RestartServerNode routine

        pass

    def test91_StopServerNode(self):
        #write code for testing StopServerNode routine
        request = types.RequestStopServerNode(auth=AUTH)
        response = APP.StopServerNode(request)

        self.assertEquals(response.ret_code, 0, response.ret_message)

