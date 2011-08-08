"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.nodesManager.plugins.base_operations
@author Konstantin Andrusenko
@date August 9, 2011

This module contains the implementation of basic nodes operations
"""
from blik.nodesManager.operationsPlugin import OperationPlugin, CLUSTER

#config objects types
CLUSTER_CONFIG_TYPE  = 1
NODE_CONFIG_TYPE = 2


class SynchronizeOperation(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        if call_object.object == CLUSTER:
            raise Exception('Synchronize operation should be runned on one node only!')

        if len(call_object.object_value) > 1:
            raise Exception('Synchronize operation should be runned on one node only!')

        node = call_object.object_value[0]

        rows = self.dbConn.select('SELECT N.id, N.logic_name, N.architecture, NT.name, \
                    C.cluster_sid FROM nm_node N, nm_node_type NT, nm_cluster C\
                    FROM C.id=N.cluster_id AND NT.id=N.node_type AND hostname=%s', (node,))

        if not rows:
            raise Exception('Node with hostname %s is not found in database!'%node)

        node_id, logic_name, arch, type_name, cluster_sid = rows[0]


        #select node config parameters
        rows = self.dbConn.select('SELECT CS.parameter_name, C.parameter_value \
                                    FROM nm_config_spec CS, nm_config C \
                                    WHERE CS.object_type_id=%s AND C.object_id=%s',
                                    (NODE_CONFIG_TYPE, node_id ))

        in_params = {'logic_name': logic_name,
                     'arch': arch,
                     'node_type': type_name,
                     'cluster_sid': cluster_sid}

        for name, value in rows:
            in_params[name] = value

        parameters.update(in_params)


    def onCallResults(self, operation, status, ret_parameters):
        pass


class RebootOperation(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        operations = self.checkRunnedOperations(call_object)

        if operations:
            raise Exception('Reboot is not runned, found inprogress operations in cluster! \
                            Wait operations finish and try again.')

    def onCallResults(self, operation, status, ret_parameters):
        pass

