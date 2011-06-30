#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.operationsEngine
@author Konstantin Andrusenko
@date July 3, 2011

This module contains the implementation for the OperationsEngine class.

"""
from datetime import datetime, timedelta
from Queue import Queue
import threading
import thread
import time
import friClientLibrary
from friClientLibrary import FriClient
from blik.utils.config import Config
from blik.utils.logger import logger
from blik.utils.databaseConnection import DatabaseConnection

#operation result statuses
ORS_INPROGRESS  = 0
ORS_COMPLETE    = 1
ORS_TIMEOUTED   = 2

class OperationResult:
    def __init__(self, operation_timeout, callbackFunction):
        self.ret_params_map = {} #FIXME: should be thread-safe
        self.max_end_datetime = datetime.now() + timedelta(0, operation_timeout)
        self.callbackFunction = callbackFunction

class Node:
    def __init__(self, id, hostname):
        self.id = id
        self.hostname = hostname

class OperationsEngine:
    def __init__(self):
        self.__check_op_timeouts_thread = None
        self._fri_client = None
        self._dbconn = DatabaseConnection()
        self._active_operations = OperationsMap()

        #start thread for checking timeouted operations
        self.__check_op_timeouts_thread = CheckOpTimeoutsThread(self._active_operations)
        self.__check_op_timeouts_thread.setName('operationsEngine.CheckOpTimeoutsThread')
        self.__check_op_timeouts_thread.start()

        self._fri_client = WrappedFriClient(self._active_operations, self._dbconn)

        self._fri_client.start(Config.oper_callers_count, Config.oper_results_threads)

    def __del__(self):
        if self.__check_op_timeouts_thread:
            self.__check_op_timeouts_thread.stop()

        if self._fri_client:
            self._fri_client.stop()

    def __insert_operation_into_db(self, operation_id, user_name, nodes):
        self._dbconn.start_transaction()
        try:
            rows = self._dbconn.modify_fetch("INSERT INTO NM_OPERATION_INSTANCE (operation_id, start_datetime, status, initiator_id) \
                                VALUES (%s,%s,%s,(SELECT id FROM NM_USER WHERE name=%s)) RETURNING id",
                                (operation_id, datetime.now(), ORS_INPROGRESS, user_name))

            session_id = rows[0][0]

            for node in nodes:
                self._dbconn.modify("INSERT INTO NM_OPERATION_PROGRESS (node_id, instance_id, status)\
                                    VALUES (%s, %s, %s)", (node.id, session_id, ORS_INPROGRESS))

            return session_id
        finally:
            self._dbconn.end_transaction()

    def __delete_session(self, session_id):
        self._dbconn.start_transaction()
        try:
            self._dbconn.modify("DELETE FROM NM_OPERATION_PROGRESS WHERE instance_id=%s", (session_id,))

            self._dbconn.modify("DELETE FROM NM_OPERATION_INSTANCE WHERE id=%s", (session_id,))
        except Exception, err:
            logger.error('OperationsEngine.__delete_session: %s'%err)
        finally:
            self._dbconn.end_transaction()


    def __form_nodes(self, rows, node_type_id):
        nodes = []
        for row in rows:
            if node_type_id and (row[2] != node_type_id):
                continue

            node = Node(row[0], row[1])
            nodes.append(node)

        return nodes

    def __call_operation(self, session_id, nodes, operation_name, parameters_map):
        hostnames = [n.hostname for n in nodes]

        ret_code, ret_message = self._fri_client.operationCall(session_id, hostnames, operation_name, parameters_map)

        if ret_code != friClientLibrary.RC_OK:
            raise Exception(ret_message)


    def __get_operation_info(self, operation_name):
        rows = self._dbconn.select("SELECT id, node_type_id, timeout FROM NM_OPERATION WHERE name=%s",(operation_name,))
        if not rows:
            raise Exception('Operation with name %s is not found in database!' % operation_name)

        return rows[0][0], rows[0][1], rows[0][2]


    def getOperationStatus(self, session_id):
        '''
        get status of operation instance

        @session_id (integer) identifier of operation instance (nm_operation_instance.id)

        @return status of operation instance
        '''
        try:
            rows = self._dbconn.select("SELECT status FROM NM_OPERATION_INSTANCE WHERE id=%s",(session_id,))

            if not rows:
                raise Exception('Operation instance with ID=%s is not found in database!' % session_id)

            return rows[0][0]
        except Exception, err:
            logger.error('getOperationStatus: %s'%err)

    def callOperationOnCluster(self, user_name, cluster_name, operation_name, parameters_map, onOperationResultRoutine):
        '''
        call operation on all nodes in cluster

        @user_name (string) name of user who calling operation (nm_user.name)
        @cluster_name (string) name of cluster (nm_cluster.cluster_sid)
        @operation_name (string) name of operatiob (nm_operation.name)
        @parameters_map (dict {param_name, param_value}) operation input parameters
        @onOperationResultRoutine (func) callback routine for receiving operation results
                            This routine should has following spec: (status, ret_params_map),
                            where status (integer) - status of operation
                            ret_params_map (dict) - {<node_hostname>: { <param_name> : <param_value>, ...}, ...}

        @return (session_id, ret_code, ret_message)
        '''
        try:
            session_id = None
            logger.info('CALL operation %s on cluster %s'%(operation_name, cluster_name))

            operation_id, node_type_id, timeout = self.__get_operation_info(operation_name)

            rows = self._dbconn.select("SELECT N.id, N.hostname, N.node_type FROM NM_NODE N, NM_CLUSTER C \
                                        WHERE C.id = N.cluster_id AND C.cluster_sid=%s",(cluster_name,))
            if not rows:
                raise Exception('No nodes found for cluster with name %s' % cluster_name)

            nodes = self.__form_nodes(rows, node_type_id)
            if not nodes:
                raise Exception('Not found nodes for operation %s in cluster %s.'%(operation_name, cluster_name))

            session_id = self.__insert_operation_into_db(operation_id, user_name, nodes)

            self._active_operations.put(session_id, OperationResult(timeout, onOperationResultRoutine))

            self.__call_operation(session_id, nodes, operation_name, parameters_map)

            return (session_id, 0, 'Operation %s is called on cluster %s' % (operation_name, cluster_name))
        except Exception, err:
            logger.error('callOperationOnCluster error: %s' % err)
            if session_id:
                self._active_operations.delete(session_id)
                self.__delete_session(session_id)

            return (None, 1, str(err))

    def callOperationOnNodes(self, user_name, nodes_list, operation_name, parameters_map, onOperationResultRoutine):
        '''
        call operation on all nodes in cluster

        @user_name (string) name of user who calling operation (nm_user.name)
        @nodes_list (list of strings) hostnames of nodes (nm_node.hostname)
        @operation_name (string) name of operatiob (nm_operation.name)
        @parameters_map (dict {param_name, param_value}) operation input parameters
        @onOperationResultRoutine (func) callback routine for receiving operation results
                            This routine should has following spec: (status, ret_params_map),
                            where status (integer) - status of operation
                            ret_params_map (dict) - {<node_name>: { <param_name> : <param_value>, ...}, ...}

        @return (session_id, ret_code, ret_message)
        '''
        try:
            session_id = None
            logger.info('CALL operation %s on nodes %s'%(operation_name, nodes_list))

            operation_id, node_type_id, timeout = self.__get_operation_info(operation_name)

            rows = self._dbconn.select("SELECT id, hostname, node_type FROM NM_NODE \
                                        WHERE hostname IN (%s)" % ','.join(["'%s'"%n for n in nodes_list]))
            if not rows:
                raise Exception('No nodes found with hostnames %s in database' % nodes_list)

            nodes = self.__form_nodes(rows, node_type_id)
            if not nodes:
                raise Exception('Not found nodes for operation %s.'%(operation_name,))

            session_id = self.__insert_operation_into_db(operation_id, user_name, nodes)

            self._active_operations.put(session_id, OperationResult(timeout, onOperationResultRoutine))

            self.__call_operation(session_id, nodes, operation_name, parameters_map)

            return (session_id, 0, 'Operation %s is called on nodes' % (operation_name,))
        except Exception, err:
            logger.error('calOperationOnNodes error: %s' % err)
            if session_id:
                self._active_operations.delete(session_id)
                self.__delete_session(session_id)
            return (None, 1, str(err))


    def callOperationOnNode(self, user_name, node_hostname, operation_name, parameters_map, onOperationResultRoutine):
        '''
        call operation on all nodes in cluster

        @user_name (string) name of user who calling operation (nm_user.name)
        @node_name (string) hostname of node (nm_node.hostname)
        @operation_name (string) name of operatiob (nm_operation.name)
        @parameters_map (dict {param_name, param_value}) operation input parameters
        @onOperationResultRoutine (func) callback routine for receiving operation results
                            This routine should has following spec: (status, ret_params_map),
                            where status (integer) - status of operation
                            ret_params_map (dict) - {<node_name>: { <param_name> : <param_value>, ...}, ...}

        @return (session_id, ret_code, ret_message)
        '''
        try:
            session_id = None
            logger.info('CALL operation %s on node %s'%(operation_name, node_hostname))

            operation_id, node_type_id, timeout = self.__get_operation_info(operation_name)

            rows = self._dbconn.select("SELECT id, hostname, node_type FROM NM_NODE \
                                        WHERE hostname=%s", (node_hostname,))
            if not rows:
                raise Exception('No nodes found with hostname %s in database' % node_hostname)

            nodes = self.__form_nodes(rows, node_type_id)
            if not nodes:
                raise Exception('Not found node for operation %s.'%(operation_name,))

            session_id = self.__insert_operation_into_db(operation_id, user_name, nodes)

            self._active_operations.put(session_id, OperationResult(timeout, onOperationResultRoutine))

            self.__call_operation(session_id, nodes, operation_name, parameters_map)

            return (session_id, 0, 'Operation %s is called on nodes' % (operation_name,))
        except Exception, err:
            logger.error('calOperationOnNode error: %s' % err)
            if session_id:
                self._active_operations.delete(session_id)
                self.__delete_session(session_id)
            return (None, 1, str(err))


class WrappedFriClient(FriClient):
    def __init__(self, active_operations, dbconn):
        self._active_operations = active_operations
        self._dbconn = dbconn

        FriClient.__init__(self)

    def _update_operation_progress(self, session_id, node, ret_code, ret_message):
        '''
        update operation progress in database (NM_OPERATION_PROGRESS table)

        @return True if operation is completed or False if operation in progress
        '''
        try:
            self._dbconn.modify("UPDATE NM_OPERATION_PROGRESS SET status=%s, ret_code=%s, ret_message=%s \
                                   WHERE instance_id=%s AND node_id=(SELECT id FROM NM_NODE WHERE hostname=%s)",
                                   (ORS_COMPLETE, ret_code, ret_message, session_id, node))

            uncompleted_count = self._dbconn.select("SELECT count(id) FROM NM_OPERATION_PROGRESS \
                                    WHERE instance_id=%s AND status=%s", (session_id,ORS_INPROGRESS))

            if uncompleted_count[0][0] == 0:
                return True
            return False
        except Exception, err:
            logger.error('WrappedFriClient._update_operation_progress: %s'%err)
            raise err

    def _finish_operation(self, session_id, operation):
        try:
            self._dbconn.modify("UPDATE NM_OPERATION_INSTANCE SET status=%s, end_datetime=%s WHERE id=%s",
                                (ORS_COMPLETE, datetime.now(), session_id))

            self._active_operations.delete(session_id)

            operation.callbackFunction(session_id, ORS_COMPLETE, operation.ret_params_map)
        except Exception, err:
            logger.error('WrappedFriClient._finish_operation: %s'%err)
            raise err

    def onAsyncOperationResult(self, session_id, node, ret_code, ret_message, ret_params_map):
        '''
        Reimplemented FriClient class method for performing asynchronous operation results

        @session_id (string) identifier of session (operation instance id)
        @ret_code (integer) code of result
        @ret_message (string) result description
        @ret_params_map (dict {<param_name>:<param_value>}) return parameters
        '''
        try:
            operation = self._active_operations.get(session_id, None)
            if operation is None:
                logger.error('onAsyncOperationResult failed: Operation instance with ID=%s is not found.\
                            Received parameters: node=%s, ret_code=%s, ret_message=%s, ret_params_map=%s'%\
                            (node, ret_code, ret_message, ret_params_map))
                return

            operation.ret_params_map[node] = ret_params_map

            is_completed = self._update_operation_progress(session_id, node, ret_code, ret_message)

            if is_completed:
                self._finish_operation(session_id, operation)
        except:
            pass


class CheckOpTimeoutsThread(threading.Thread):
    """Thread class for checking operations timeouts"""

    def __init__(self, active_operations):
        self._active_operations = active_operations
        self._is_started = True
        self._dbconn = DatabaseConnection()

        # Initialize the thread 
        threading.Thread.__init__(self)

    def _finish_operation(self, session_id, operation):
        try:
            self._dbconn.modify("UPDATE NM_OPERATION_INSTANCE SET status=%s, end_datetime=%s WHERE id=%s",
                                (ORS_TIMEOUTED, datetime.now(), session_id))

            self._dbconn.modify("UPDATE NM_OPERATION_PROGRESS SET status=%s, ret_code=%s, ret_message=%s \
                                   WHERE instance_id=%s AND status=%s",
                                   (ORS_TIMEOUTED, 12, 'Operation is timeouted!', session_id, ORS_INPROGRESS))

            self._active_operations.delete(session_id)

            operation.callbackFunction(session_id, ORS_TIMEOUTED, operation.ret_params_map)
        except Exception, err:
            logger.error('CheckOpTimeoutsThread._finish_operation: %s'%err)


    def stop(self):
        self._is_started = False

    def _update_pending_operations(self):
        try:
            dbconn = DatabaseConnection()

            dbconn.modify("UPDATE NM_OPERATION_INSTANCE SET status=%s, end_datetime=%s WHERE status=%s",
                            (ORS_TIMEOUTED, datetime.now(), ORS_INPROGRESS,))
            dbconn.modify("UPDATE NM_OPERATION_PROGRESS SET status=%s, ret_code=%s, ret_message=%s \
                            WHERE status=%s",(ORS_TIMEOUTED, 12, 'Operation is timeouted!', ORS_INPROGRESS))
            del dbconn
        except Exception, err:
            logger.error('CheckOpTimeoutsThread._update_pending_operations: %s'%err)


    def run(self):
        logger.debug('%s started!'%self.getName())

        self._update_pending_operations()

        while self._is_started:
            try:
                (session_id, operation) = self._active_operations.get_timeouted_operation()

                if not session_id:
                    time.sleep(1)
                    continue

                self._finish_operation(session_id, operation)
            except Exception, err:
                err_message = '%s failed: %s'%(self.getName(), err)
                logger.error(err_message)


class OperationsMap:
    def __init__(self):
        self.__map = {}
        self.__lock = thread.allocate_lock()

    def get(self, key, default=None):
        self.__lock.acquire_lock()
        try:
            return self.__map.get(key, default)
        finally:
            self.__lock.release_lock()

    def put(self, key, value):
        self.__lock.acquire_lock()
        try:
            self.__map[key] = value
        finally:
            self.__lock.release_lock()

    def delete(self, key):
        self.__lock.acquire_lock()
        try:
            if self.__map.has_key(key):
                del self.__map[key]
        finally:
            self.__lock.release_lock()

    def get_timeouted_operation(self):
        self.__lock.acquire_lock()
        try:
            sess_id = None
            oper = None

            for session_id, operation in self.__map.items():
                if operation.max_end_datetime < datetime.now():
                    sess_id = session_id
                    oper = operation
                    break

            return sess_id, oper
        finally:
            self.__lock.release_lock()

