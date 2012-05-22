#!/usr/bin/python
"""
Copyright (C) 2012 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.management.core.system_api
@author Konstantin Andrusenko
@date May 26, 2012

This module contains the SystemAPI class implementation
for managing system information in management database
"""

from blik.management.core import BaseManagementAPI, auth
from blik.management.core.models import NmClusterType, NmConfigSpec, NmClusterTypeNodes, \
                                        NmNodeType, ObjectDoesNotExist

CUST_ROLE = 'customizator'

CLUSTER_TYPE_OBJ = 1
NODE_TYPE_OBJ = 2

PARAM_TYPES_MAP = { 'string': 1,
                    'integer': 2 }

PARAM_TYPES_MAP_REV = { 1 : 'string',
                        2 : 'integer' }

class SystemAPI(BaseManagementAPI):
    @auth(CUST_ROLE)
    def register_cluster_type(self, cluster_type_sid, allowed_nodes_types, parameters_spec, description):
        cluster_type = None
        objects = NmClusterType.objects.filter(type_sid=cluster_type_sid)
        if objects:
            cluster_type = objects[0]
            cluster_type.description = description
        else:
            cluster_type = NmClusterType(type_sid=cluster_type_sid, description=description)

        cluster_type.save()


        #setup specifications of parameters for cluster type
        for param_spec in parameters_spec:
            objects = NmConfigSpec.objects.filter(config_object=CLUSTER_TYPE_OBJ, object_type_id=cluster_type.id, parameter_name=param_spec.name)
            if objects:
                param = objects[0]
            else:
                param = NmConfigSpec()
                param.config_object = CLUSTER_TYPE_OBJ
                param.object_type_id = cluster_type.id
                param.parameter_name = param_spec.name

            param.parameter_type = PARAM_TYPES_MAP[param_spec.type]
            param.posible_values_list = '|'.join(param_spec.posible_params)
            param.default_value = param_spec.default
            param.save()

        #setup allowed nodes types
        for node_type_sid in allowed_nodes_types:
            try:
                node_type = NmNodeType.objects.get(type_sid=node_type_sid)
            except ObjectDoesNotExist:
                raise Exception('Node type with SID "%s" does not found!'% node_type_sid)

            if not NmClusterTypeNodes.objects.filter(node_type=node_type, cluster_type=cluster_type):
                NmClusterTypeNodes(node_type=node_type, cluster_type=cluster_type).save()


    @auth(CUST_ROLE)
    def get_cluster_type(self, cluster_type):
        objects = NmClusterType.objects.filter(type_sid=cluster_type)
        if not objects:
            raise RuntimeError('Cluster type with SID "%s" does not found!'%cluster_type)

        cluster_type = objects[0]

        allowed_nodes = NmClusterTypeNodes.objects.filter(cluster_type=cluster_type)
        param_specs = NmConfigSpec.objects.filter(config_object=CLUSTER_TYPE_OBJ, object_type_id=cluster_type.id)
        ret_param_specs = []
        for param_spec in param_specs:
            if param_spec.posible_values_list:
                pos_values = param_spec.posible_values_list.split('|')
            else:
                pos_values = []

            ret_param_specs.append({'name': param_spec.parameter_name,
                                    'type': PARAM_TYPES_MAP_REV[param_spec.parameter_type],
                                    'posible_values': pos_values,
                                    'default': param_spec.default_value})

        return cluster_type.type_sid, ret_param_specs, [an.node_type.type_sid for an in allowed_nodes], cluster_type.description

