#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.bootManager.bootEventListener
@author Konstantin Andrusenko
@date July 28, 2011

This module contains the implementation of BootEventListener class.
"""

import sys
from blik.utils.daemonBase import Daemon
from blik.utils.friBase import FriServer
from blik.utils.databaseConnection import DatabaseConnection
from blik.utils.logger import logger

LISTENER_PORT = 1986

#node admin states
NAS_NEW       = 0
NAS_ACTIVE    = 1
NAS_NOTACTIVE  = 2

class BootEventListener(FriServer):
    def __init__(self):
        FriServer.__init__(self, hostname='0.0.0.0', port=LISTENER_PORT, workers_count=1)
        self.__dbconn = DatabaseConnection()

    def onDataReceive( self, json_object ):
        #get hostname
        hostname = self.__get_element(json_object, 'hostname')

        #get ip_address (this field is optional)
        ip_address = json_object.get('ip_address', None)

        #get login
        login = self.__get_element(json_object, 'login')

        #get password
        password = self.__get_element(json_object, 'password')

        #get processor
        processor = self.__get_element(json_object, 'processor')

        #get memory
        memory = self.__get_element(json_object, 'memory')

        #get mac_address
        mac_address = self.__get_element(json_object, 'mac_address')

        #get uuid
        uuid = self.__get_element(json_object, 'uuid')

        #process boot event
        self.__process_event(uuid, hostname, login, password, mac_address, ip_address, processor, memory)


    def __get_element(self, json_object, name):
        element = json_object.get(name, None)
        if element is None:
            raise Exception('Element <%s> is not found in boot event packet!'%name)

        return element.strip()

    def __process_event(self, uuid, hostname, login, password, mac_address, ip_address, processor, memory):
        hw_info = 'Processor: %s\nMemory: %s'%(processor, memory)

        rows = self.__dbconn.select("SELECT id FROM nm_node WHERE node_uuid=%s", (uuid,))

        if not rows:
            #this is new node, create it in database in NEW status
            self.__dbconn.modify("INSERT INTO nm_node (node_uuid, hostname, login, password, mac_address, ip_address, admin_status, hw_info)\
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                    (uuid, hostname, login, password, mac_address, ip_address, NAS_NEW, hw_info))

        else:
            #we already has this node in database, update it
            self.__dbconn.modify("UPDATE nm_node SET hostname=%s, login=%s, password=%s, mac_address=%s, ip_address=%s, hw_info=%s\
                                    WHERE node_uuid=%s", (hostname, login, password, mac_address, ip_address, hw_info, uuid))


#--------------------------------------------------------------------------------


class BootEventListenerDaemon(Daemon):
    def onExit(self):
        try:
            logger.info('Boot event listener stoping...')
            self.listener.stop()
            logger.info('Boot event listener stoped')
        except Exception, err:
            logger.error('Stoping boot event listener error: %s'%err)

    def run(self):
        logger.info('Boot event listener starting...')

        self.listener = BootEventListener()

        self.listener.start()


if __name__ == "__main__":
    daemon = BootEventListenerDaemon('/tmp/boot-event-listener-daemon.pid', stop_timeout=5)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
