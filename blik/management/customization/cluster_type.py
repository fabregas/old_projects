#!/usr/bin/python
"""
Copyright (C) 2012 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.management.customization.cluster_type
@author Konstantin Andrusenko
@date May 11, 2012

This module contains ClusterType class implementation.
This class should be used for all operations with cluster type (insert/update/delete/get info)
"""

from blik.utils.yaml_utils import YamlFile
from blik.management.core.system_api import SystemAPI

PROP_CLUSTER_INFO = 'cluster_info'
PROP_TYPE_NAME = 'type_name'
PROP_DESCRIPTION = 'description'
PROP_ALLOWED_NODES = 'allowed_nodes'
PROP_PARAMETERS = 'parameters'
PROP_PARAM_NAME = 'name'
PROP_PARAM_TYPE = 'type'
PROP_PARAM_POS_VALS = 'posible_values'
PROP_PARAM_DEFAULT = 'default'

class ParameterSpec:
    def __init__(self, dict_params):
        self.name = dict_params[PROP_PARAM_NAME]
        self.type = dict_params[PROP_PARAM_TYPE]
        self.posible_params = [str(i) for i in dict_params.get(PROP_PARAM_POS_VALS, [])]
        self.default = dict_params.get(PROP_PARAM_DEFAULT, None)
        if self.default is not None:
            self.default = str(self.default)

        self.validate()

    def to_dict(self):
        return { PROP_PARAM_NAME: self.name,
                 PROP_PARAM_TYPE: self.type,
                 PROP_PARAM_POS_VALS: self.posible_params,
                 PROP_PARAM_DEFAULT: self.default }

    def validate(self):
        if not self.name:
            raise RuntimeError('Parameter specification name is empty!')

        if self.type not in ['string', 'integer']:
            raise RuntimeError('Parameter specification type "%s" is not supported!'% self.type)

        if type(self.posible_params) != list:
            raise RuntimeError('Possible values should has list type')

        if self.posible_params and self.default and self.default not in self.posible_params:
            raise RuntimeError('Default value "%s" does not specified in posible values list: %s'\
                                                            %(self.default, self.posible_params))



class ClusterType:
    def __init__(self):
        self.type_name = None
        self.description = None
        self.allowed_nodes = [] #if nodes list is empty - all nodes are allowed
        self.parameters = []

        self.__system_api = SystemAPI()

    def load_from_file(self, yaml_file):
        yaml_file = YamlFile(yaml_file)
        yaml_file.parse()

        cluster_info = yaml_file.get_object(PROP_CLUSTER_INFO)
        self.type_name = cluster_info[PROP_TYPE_NAME]
        self.description = cluster_info[PROP_DESCRIPTION]
        self.allowed_nodes = cluster_info.get(PROP_ALLOWED_NODES, [])

        params = cluster_info.get(PROP_PARAMETERS, [])
        self.parameters = [ParameterSpec(d_val) for d_val in params]

    def save_to_file(self, file_path):
        cluster_info = { PROP_TYPE_NAME: self.type_name,
                         PROP_DESCRIPTION: self.description,
                         PROP_ALLOWED_NODES: self.allowed_nodes,
                         PROP_PARAMETERS: [p.to_dict() for p in self.parameters] }

        yaml_file = YamlFile(file_path)
        yaml_file.load_objects({PROP_CLUSTER_INFO: cluster_info})
        yaml_file.save()


    def load_from_database(self, cluster_type):
        self.type_name, parameters, self.allowed_nodes, self.description = \
                                self.__system_api.get_cluster_type(cluster_type)

        self.parameters = []
        for param in parameters:
            self.parameters.append(ParameterSpec(param))

    def save_into_database(self):
        self.__system_api.register_cluster_type(self.type_name, \
                    self.allowed_nodes, self.parameters, self.description)
