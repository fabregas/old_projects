from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

import unittest
from blik.nodesManager.plugins import base_operations
from blik.nodesManager.operationsPluginManager import CallObject
from blik.utils.databaseConnection import DatabaseConnection

dbconn = DatabaseConnection()

base_operations.SynchronizeOperation.dbConn = dbconn
base_operations.RebootOperation.dbConn = dbconn
base_operations.ModHostnameOperation.dbConn = dbconn

class BaseClusterOperationsTestCase(unittest.TestCase):
    def test01_sync_operation(self):
        sync_oper = base_operations.SynchronizeOperation()

        call_object = CallObject(CallObject.CLUSTER, 'TEST_CLUSTER')

        try:
            sync_oper.beforeCall('SYNC', call_object, {})
        except Exception, err:
            print ('EXPECTED exception: %s'%err)
        else:
            raise Exception('should be exception in this case')


        call_object = CallObject(CallObject.NODES, ['node-01','node-02'])
        try:
            sync_oper.beforeCall('SYNC', call_object, {})
        except:
            print ('EXPECTED exception: %s'%err)
        else:
            raise Exception('should be exception in this case')


        call_object = CallObject(CallObject.NODES, ['node-01'])
        ret_code, ret_message = sync_oper.beforeCall('SYNC', call_object, {})
        self.assertNotEqual(ret_code, 0, ret_message)

        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        params = {}
        ret = sync_oper.beforeCall('SYNC', call_object, params)
        self.assertEqual(ret, None)
        self.assertNotEqual(params, {})
        self.assertEqual(params['cluster_sid'], 'TEST_CLUSTER')
        self.assertEqual(params['logic_name'], 'test_node_1')
        self.assertEqual(params['arch'], 'x86')
        self.assertEqual(params['node_type'], 'COMMON')
        print params

    def test02_reboot_operation(self):
        reboot_op = base_operations.RebootOperation()

        call_object = CallObject(CallObject.CLUSTER, 'TEST_CLUSTER')
        ret = reboot_op.beforeCall('REBOOT', call_object, {})
        self.assertEqual(ret, None)

        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        ret = reboot_op.beforeCall('REBOOT', call_object, {})
        self.assertEqual(ret, None)

        dbconn.modify('UPDATE nm_operation_instance SET status=0')
        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        try:
            ret = reboot_op.beforeCall('REBOOT', call_object, {})
        except Exception, err:
            print ('EXPECTED exception: %s'%err)
        else:
            raise Exception('should be exception in this case')

        dbconn.modify('UPDATE nm_operation_instance SET status=1')

    def test03_modhost_operation(self):
        mod_host_op = base_operations.ModHostnameOperation()

        call_object = CallObject(CallObject.CLUSTER, 'TEST_CLUSTER')
        try:
            mod_host_op.beforeCall('MOD_HOSTNAME', call_object, {})
        except Exception, err:
            print ('Expected exception: %s'%err)
        else:
            raise Exception('should be exception in this case')

        call_object = CallObject(CallObject.NODES, ['node-01', 'node-02'])
        try:
            mod_host_op.beforeCall('MOD_HOSTNAME', call_object, {})
        except Exception, err:
            print ('Expected exception: %s'%err)
        else:
            raise Exception('should be exception in this case')


        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        try:
            mod_host_op.beforeCall('MOD_HOSTNAME', call_object, {})
        except Exception, err:
            print ('Expected exception: %s'%err)
        else:
            raise Exception('should be exception in this case')


        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        try:
            mod_host_op.beforeCall('MOD_HOSTNAME', call_object, {'hostname':'test_bad_hostname'})
        except Exception, err:
            print ('Expected exception: %s'%err)
        else:
            raise Exception('should be exception in this case')

        call_object = CallObject(CallObject.NODES, ['127.0.0.1'])
        ret = mod_host_op.beforeCall('MOD_HOSTNAME', call_object, {'hostname':'test-hostname'})
        self.assertEqual(ret, None)


        #on receive

        ret = mod_host_op.onCallResults('MOD_HOSTNAME', 666, 1, {})
        self.assertEqual(ret, 1)

        ret = mod_host_op.onCallResults('MOD_HOSTNAME', 666, 1, {'test-node':{'hostname':'test-node-01'}})
        self.assertEqual(ret, None)


if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################
