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
from blik.utils.logger import logger

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
                    WHERE C.id=N.cluster_id AND NT.id=N.node_type AND N.hostname=%s', (node,))

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




############## REBOOT ##############################################

class RebootOperation(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        operations = self.checkRunnedOperations(call_object)

        if operations:
            raise Exception('Reboot is not runned, found inprogress operations in cluster! \
                            Wait operations finish and try again.')


############## MOD_HOSTNAME ##############################################

class ModHostnameOperation(OperationPlugin):
    def beforeCall(self, operation, call_object, parameters):
        if call_object.object == CLUSTER:
            raise Exception('Modifying hostname operation should be runned on one node only!')

        if len(call_object.object_value) > 1:
            raise Exception('Modifying hostname operation should be runned on one node only!')


        if not parameters.has_key('hostname'):
            raise Exception('Mandatory parameter "hostname" is not found!')

        hostname = parameters['hostname'].strip()

        if len(hostname) == 0:
            raise Exception('Hostname is empty!')

        if not re.match('[a-zA-Z][a-zA-Z0-9\-]+$', hostname):
            raise Exception('Hostname is invalid. Allowed characters are: a-z, A-Z, 0-9 and "-"')

        #check already exists hostname in DB
        rows = self.dbConn.select('SELECT id FROM nm_node WHERE hostname=%s', (hostname,))

        if rows:
            raise Exception('Hostname %s is already used by another node!' % hostname)


    def onCallResults(self, operation, session_id, status, ret_parameters):
        if status != OperationPlugin.OS_COMPLETED:
            return

        try:
            if len(ret_parameters) != 1:
                raise Exception('Received parameters is not valid! Expected hostname parameter from node.')

            params = ret_parameters.values()[0]
            if not params.has_key('hostname'):
                raise Exception('Expected hostname parameter from node. But received: %s'%params)

            hostname = params['hostname']

            self.dbConn.modify('UPDATE nm_node SET hostname=%s WHERE id = \
                                (SELECT node_id FROM nm_operation_progress WHERE instance_id=%s)',
                                (hostname, session_id))
        except Exception, err:
            logger.error('Chaning node hostname (in database) failed. Details: %s'%err)

