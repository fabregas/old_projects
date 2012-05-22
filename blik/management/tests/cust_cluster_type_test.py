import os
import unittest
import tempfile

from blik.utils.config import Config
Config.db_name = 'blik_cloud_db_test'

from blik.management.core.models import *
from blik.management.customization.cluster_type import ClusterType, ParameterSpec
from blik.management.core.system_api import SystemAPI
from blik.management.core.models import NmNodeType


TEST_CLUSTER_1_SPEC_FILE = 'cluster01.yaml'
TEST_CLUSTER_2_SPEC_FILE = 'cluster02.yaml'
TEST_CLUSTER_2_SPEC_FILE_U = 'cluster02_upd.yaml'
TEST_CLUSTER_3_SPEC_FILE = 'cluster03.yaml'


class Session:
    def authorize(self, role):
        return True

SystemAPI.init_global_session(Session())

class TestCustomClusterType(unittest.TestCase):
    def __check_2_specs(self, cluster_type, cluster_type2):
        self.assertEqual(cluster_type.type_name, cluster_type2.type_name)
        self.assertEqual(cluster_type.description, cluster_type2.description)
        self.assertEqual(cluster_type.allowed_nodes, cluster_type2.allowed_nodes)
        self.assertEqual(len(cluster_type.parameters), len(cluster_type2.parameters))

        for i, param in enumerate(cluster_type.parameters):
            self.assertEqual(param.name, cluster_type2.parameters[i].name)
            self.assertEqual(param.type, cluster_type2.parameters[i].type)
            self.assertEqual(param.default, cluster_type2.parameters[i].default)
            self.assertEqual(param.posible_params, cluster_type2.parameters[i].posible_params)

    def test_yaml_load(self):
        cluster_type = ClusterType()

        cluster_spec_file = os.path.join(os.path.dirname(__file__), TEST_CLUSTER_1_SPEC_FILE)
        cluster_type.load_from_file(cluster_spec_file)

        self.assertEqual(cluster_type.type_name, 'cluster01')
        self.assertEqual(cluster_type.description, 'Test cluster #1 for UT')
        self.assertEqual(cluster_type.allowed_nodes, ['node_type_01', 'node_type_02'])
        for param in cluster_type.parameters:
            if param.name == 'str_param':
                self.assertEqual(param.type, 'string')
                self.assertEqual(param.default, 'default value')
                self.assertEqual(param.posible_params, [])
            elif param.name == 'int_param':
                self.assertEqual(param.type, 'integer')
                self.assertEqual(param.default, '0')
                self.assertEqual(param.posible_params, ['0', '1', '2', '3'])
            else:
                raise RuntimeError('Unexpected parameter "%s"'%(param.name))


    def test_yaml_save(self):
        cluster_type = ClusterType()
        cluster_spec_file = os.path.join(os.path.dirname(__file__), TEST_CLUSTER_1_SPEC_FILE)
        cluster_type.load_from_file(cluster_spec_file)

        tmp_file, path = tempfile.mkstemp('test_yaml_save')

        cluster_type.save_to_file(path)

        cluster_type2 = ClusterType()
        cluster_type2.load_from_file(path)

        self.__check_2_specs(cluster_type, cluster_type2)


    def test_03_save_into_database(self):
        NmNodeType(type_sid='node_type_01').save()
        NmNodeType(type_sid='node_type_02').save()

        cluster_type = ClusterType()
        cluster_spec_file = os.path.join(os.path.dirname(__file__), TEST_CLUSTER_1_SPEC_FILE)
        cluster_type.load_from_file(cluster_spec_file)

        cluster_type.save_into_database()

        cluster_type2 = ClusterType()
        cluster_type2.load_from_database('cluster01')

        self.__check_2_specs(cluster_type, cluster_type2)

if __name__ == '__main__':
    unittest.main()
