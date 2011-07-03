#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.nodesMonitor
@author Konstantin Andrusenko
@date July 9, 2011

This module contains the implementation of NodesMonitor class.
    NodesMonitor is thread that monitor nodes states and update
    database (nm_node table) if state changing

"""
from datetime import datetime
from datetime import timedelta
from Queue import Queue
import threading
import time
from blik.utils.config import Config
from blik.utils.databaseConnection import DatabaseConnection
from blik.utils.logger import logger
from blik.nodesManager.friBase import FriCaller

#cluster states
CS_NOT_ACTIVE = 0
CS_ACTIVE     = 1

#admin node stated
ANS_NOT_ACTIVE = 0
ANS_ACTIVE = 1
ANS_FAILED = 2

#current node states
CNS_OFF = 0
CNS_ON  = 1

FINISH_FLAG = None


class NodesMonitor(threading.Thread):
    def __init__(self):
        self.__monitor_timeout = Config.nodes_monitor_timeout

        self.__threads = []
        self.__nodes_queue = Queue()
        self.__dbconn = DatabaseConnection()
        self.__stoped = False

        for i in xrange(Config.monitor_workers_count):
            thread = MonitorWorkerThread(self.__nodes_queue, Config.monitor_wait_response_timeout)
            thread.setName('MonitorWorkerThread#%i'%i)
            thread.start()

            self.__threads.append(thread)

        threading.Thread.__init__(self, name='NodesMonitor')

    def stop(self):
        self.__stoped = True

        for i in self.__threads:
            self.__nodes_queue.put(FINISH_FLAG)

        self.__nodes_queue.join()

    def run(self):
        logger.info('NodesMonitor started!')

        while not self.__stoped:
            try:
                t0_point = datetime.now()

                rows = self.__dbconn.select("SELECT N.hostname, N.current_state FROM nm_node N, nm_cluster C \
                                    WHERE N.cluster_id=C.id AND N.admin_status=%s AND C.status=%s",
                                    (ANS_ACTIVE, CS_ACTIVE))

                logger.debug('NodesMonitor: Selected %i nodes for checking state'%len(rows))

                for row in rows:
                    self.__nodes_queue.put((row[0], row[1]))

                self.__nodes_queue.join()

                dt = datetime.now() - t0_point
                wait_time = timedelta(0, self.__monitor_timeout) - dt
                if wait_time.days < 0:
                    #geted more then __monitor_timeout seconds for processing
                    continue

                wait_seconds = wait_time.seconds + (wait_time.microseconds * 0.000001)
                time.sleep(wait_seconds)
            except Exception, err:
                logger.error('NodesMonitor failed: %s' % err)
                time.sleep(self.__monitor_timeout)

        logger.info('NodesMonitor stoped!')



class MonitorWorkerThread(threading.Thread):
    def __init__(self, queue, wait_timeout):
        self.queue = queue
        self.wait_timeout = wait_timeout
        self.dbconn = DatabaseConnection()

        threading.Thread.__init__(self)

    def run(self):
        logger.info('%s started!'%self.getName())

        fri_caller = FriCaller()

        packet = {'id':0, 'node': '',
                  'operation': 'LIVE'}

        while True:
            try:
                item = self.queue.get()
                if item == FINISH_FLAG:
                    logger.info('%s stoped!'%self.getName())
                    break

                hostname, last_state = item

                ret_code, ret_message = fri_caller.call(hostname, packet, timeout=self.wait_timeout)

                if ret_code:
                    logger.debug('Node with hostname %s is not live!!!'%hostname)
                else:
                    logger.debug('Node with hostname %s is live!'%hostname)

                if ret_code and (last_state == CNS_ON):
                    self.__change_node_state(hostname, CNS_OFF)

                elif (not ret_code) and (last_state == CNS_OFF):
                    self.__change_node_state(hostname, CNS_ON)
            except Exception, err:
                logger.error('%s failed: %s'%(self.getName(), err))
            finally:
                self.queue.task_done()

    def __change_node_state(self, hostname, state):
        self.dbconn.modify("UPDATE nm_node SET current_state=%s WHERE hostname=%s", (state,hostname))

