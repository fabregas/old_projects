
import unittest
from blik.nodeAgent.plugins import base_operations

class SynchronizeOperationUT(base_operations.SynchronizeOperation):
    def updateOperationProgress(self, progress_percent, ret_message='', ret_code=0, ret_params={}):
        self.ret_code = ret_code
        self.progress_percent = progress_percent
        self.ret_message = ret_message
        self.ret_params = ret_params

class RebootUT(base_operations.RebootOperation):
    def updateOperationProgress(self, progress_percent, ret_message='', ret_code=0, ret_params={}):
        self.ret_code = ret_code
        self.progress_percent = progress_percent
        self.ret_message = ret_message
        self.ret_params = ret_params

class GetNodeInfoOperationUT(base_operations.GetNodeInfoOperation):
    def updateOperationProgress(self, progress_percent, ret_message='', ret_code=0, ret_params={}):
        self.ret_code = ret_code
        self.progress_percent = progress_percent
        self.ret_message = ret_message
        self.ret_params = ret_params



##########################################

class BootEventSenderThreadTestCase(unittest.TestCase):
    def test01_sync_operation(self):
        base_operations.CONFIG_FILE = '/tmp/test_node_config'
        params = {'test_param': 10, 'test_param_2':'value2'}

        sync_op = SynchronizeOperationUT(666, 'test_node')
        sync_op.process(params)

        self.assertEqual(sync_op.ret_code, 0, sync_op.ret_message)
        self.assertEqual(sync_op.progress_percent, 100)
        self.assertEqual(sync_op.ret_params, {})

        base_operations.CONFIG_FILE = '/bin/test'
        sync_op = SynchronizeOperationUT(666, 'test_node')
        sync_op.process(params)

        self.assertNotEqual(sync_op.ret_code, 0)
        self.assertEqual(len(sync_op.ret_message)> 0, True)
        self.assertEqual(sync_op.progress_percent < 100, True)
        self.assertEqual(sync_op.ret_params, {})

    def test02_reboot_operation(self):
        base_operations.run_command = lambda a: (0,'ok','')
        reboot_op = RebootUT(666, 'test_node')
        reboot_op.process({})
        self.assertEqual(reboot_op.ret_code, 0, reboot_op.ret_message)
        self.assertEqual(reboot_op.progress_percent, 100)
        self.assertEqual(reboot_op.ret_params, {})

        base_operations.run_command = lambda a: (132,'','fail')
        reboot_op = RebootUT(666, 'test_node')
        reboot_op.process({})
        self.assertNotEqual(reboot_op.ret_code,0 , reboot_op.ret_message)
        self.assertTrue('fail' in reboot_op.ret_message)
        self.assertNotEqual(reboot_op.progress_percent, 100)

    def test03_getinfo_operation(self):
        gio = GetNodeInfoOperationUT(666, 'test_node')
        gio.process({})

        self.assertEqual(gio.ret_code, 0, gio.ret_message)
        self.assertEqual(gio.progress_percent, 100)
        self.assertNotEqual(gio.ret_params, {})

        print gio.ret_params

        self.assertEqual(len(gio.ret_params) > 10, True)



if __name__ == '__main__':
    ##########################################
    unittest.main()
    ##########################################
