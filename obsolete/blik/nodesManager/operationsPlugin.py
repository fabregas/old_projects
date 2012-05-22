#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.operationsPlugin
@author Konstantin Andrusenko
@date July 5, 2011

This module contains OperationPlugin interface.
"""

#objects
CLUSTER = 1
NODES   = 2

#operation result statuses
ORS_INPROGRESS  = 0
ORS_COMPLETE    = 1
ORS_TIMEOUTED   = 2


class OperationInstance:
    def __init__(self, session_id, op_name, start_datetime, initiator_id):
        self.session_id = session_id
        self.operation_name = op_name
        self.start_datetime = start_datetime
        self.initiator_id = initiator_id


class OperationPlugin:
    dbConn = None
    operationsEngine = None

    #statuses of operation
    OS_INPROGRESS = 0
    OS_COMPLETED  = 1
    OS_TIMEOUTED  = 2

    def beforeCall(self, operation, call_object, parameters):
        '''
        This hook method call before cluster operation call
        In this method we can append/modify remove operation parameters,
                modify call_object,
                perform database operations (use dbConn),
                perform other cluster operations (use operationsEngine)
        @operation (string) - name of operation for call
        @call_object (CallObject object) - object of calling (cluster, nodes list)
        @parameters (dict {param_name: param_value}) - operation input parameters

        @return (ret_code, ret_message)
        '''
        pass

    def onCallResults(self, operation, session_id, status, ret_parameters):
        '''
        This hook method call after cluster operation call
        In this method we can append/modify remove return parameters,
            perform database operations (use dbConn),
            perform other cluster operations (use operationsEngine)
        @operation (string) - name of called operation
        @status (integer) - status of operation
        @session_id (integer) - identifier of finished operation instance
        @ret_parameters (dict {node_hostname : {param_name: param_value}}) -
            return parameters from nodes

        @return None
        '''
        pass


    def checkRunnedOperations(self, call_object, operations=[]):
        '''
        Select inprogress operations on resources described by call_object

        @call_object (CallObject object) - object of calling (cluster, nodes list)
        @operations (list of operations SIDs) - if specified, used for selecting only this inprogress operations.
                                                if equsl to [], select all inprogress operations

        @return list of inprogress operations
        '''
        if call_object.object == CLUSTER:
            rows = self.dbConn.select("SELECT N.hostname FROM nm_node N, nm_cluster C\
                            WHERE N.cluster_id=C.id AND C.cluster_sid=%s",
                            (call_object.object_value,))
            hostnames = [row[0] for row in rows]
        else:
            hostnames = call_object.object_value

        if not hostnames:
            return []

        if operations:
            oper_filter = 'AND O.sid IN (%s)' % ','.join(["'%s'"%op for op in operations])
        else:
            oper_filter = ''

        rows = self.dbConn.select('SELECT O.name, OI.id, OI.start_datetime, OI.initiator_id \
                    FROM nm_operation O, nm_operation_instance OI, nm_operation_progress OP, nm_node N \
                    WHERE O.id=OI.operation_id AND OI.id=OP.instance_id AND \
                    OI.status=%s AND OP.node_id=N.id AND N.hostname IN (%s) %s' %
                    (ORS_INPROGRESS,','.join(["'%s'"%n for n in hostnames]), oper_filter))

        op_instances = []
        for row in rows:
            op_instance = OperationInstance(row[1], row[0], row[2], row[3])
            op_instances.append(op_instance)

        return op_instances

