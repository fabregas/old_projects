from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from console_base.menu import get_menu
from console_base.auth import get_current_user, authorize
from console_base.models import *
from console_base.library import *
from copy import copy
import json
import re

try:
    from blik.nodesManager.dbusClient import DBUSInterfaceClient
    from blik.utils.exec_command import run_command
    NODES_NAMAGER_SUPPORT = True
except ImportError:
    NODES_NAMAGER_SUPPORT = False


@authorize('base')
def index(request):
    return render_to_response('base.html')

def _select_user_menu(menu, user):
    ret_menu = []
    for item in menu:
        if item['role'] not in user.roles:
            continue

        item = copy(item)
        if item.children:
            children = _select_user_menu(item.children, user)
            item.children = children

        ret_menu.append(item)

    return ret_menu



def get_menu_items(request):
    '''
    Menu example:

        [{'sid': 'test_item1',
            'label': 'Test item #1',
            'url': 'http://google.com',
            'role': none,
            'children': []
        },
        {'sid': 'test_item2',
            'role': 'admin'
            'label': 'Test item #2',
            'url': 'http://google.com',
            'children': [{
                'sid':'test_subitems1',
                'label': 'Test SUBitem #1',
                'url': 'http://google.com',
                'role': none
                'children': []
            }],
        }]
    '''
    menu = get_menu()

    user = get_current_user(request)

    user_menu = _select_user_menu(menu, user)

    return HttpResponse(json.dumps(user_menu), mimetype="application/json")


#-----------------------------------------------------------------------------------------------
# --------------------------  Clusters Management  ---------------------------------------------
#-----------------------------------------------------------------------------------------------

@authorize('clusters_ro')
def get_clusters_list(request):
    clusters = NmCluster.objects.all().order_by('id')

    return render_to_response('clusters_list.html', {'clusters':clusters})

def calculate_config_type(config):
    if config.posible_values_list:
        values = config.posible_values_list.split(LIST_PARAMETER_SPLITTER)
        if config.value in values:
            values.remove(config.value)

        config.value = [config.value] + values
        config.is_list = True

    if config.parameter_type == PT_STRING:
        config.is_string = True
    elif config.parameter_type == PT_HIDDEN_STRING:
        config.is_hidden_string = True
    elif config.parameter_type == PT_INTEGER:
        config.is_integer = True


@authorize('clusters_ro')
def configure_cluster(request, cluster_id):
    cluster = NmCluster.objects.filter(id=cluster_id)
    if not cluster:
        raise Exception('Cluster with ID=%s is not found!'%cluster_id)
    cluster = cluster[0]

    config_spec = NmConfigSpec.objects.filter(config_object=OT_CLUSTER, object_type_id=cluster.cluster_type.id)

    config = []
    cl_name = NmConfigSpec(id='clusterName', parameter_name='Cluster name', parameter_type=PT_STRING, posible_values_list='', default_value='')
    cl_name.value = cluster.cluster_name
    cl_name.is_string = True
    config.append(cl_name)

    cl_desc = NmConfigSpec(id='clusterDescr', parameter_name='Description', parameter_type=PT_STRING, posible_values_list='', default_value='')
    cl_desc.value = cluster.description
    cl_desc.is_string = True
    config.append(cl_desc)

    for spec in config_spec:
        param_value = NmConfig.objects.filter(object_id=cluster.id, parameter=spec)
        if param_value:
            spec.value = param_value[0].parameter_value
        else:
            spec.value = spec.default_value

        calculate_config_type(spec)
        config.append(spec)

    return render_to_response('cluster_config.html', {'cluster':cluster, 'config':config})

@authorize('clusters_rw')
def change_cluster_params(request, cluster_id):
    if request.method != 'POST':
        raise Exception('POST request expected for change cluster parameters!')

    cur_user = get_current_user(request)

    for key,value in request.POST.items():
        if key == 'clusterName':
            cluster = NmCluster.objects.get(id=cluster_id)
            if cluster.cluster_name == value:
                continue
            cluster.cluster_name = value
            cluster.save()
        elif key == 'clusterDescr':
            cluster = NmCluster.objects.get(id=cluster_id)
            if cluster.description == value:
                continue
            cluster.description = value
            cluster.save()
        else:
            config = NmConfig.objects.filter(object_id=cluster_id, parameter=key)
            if not config:
                config_spec = NmConfigSpec.objects.get(id=key)
                NmConfig(object_id=cluster_id, parameter=config_spec, parameter_value=value, last_modifier=cur_user).save()
            else:
                config = config[0]
                if config.parameter_value == value:
                    continue
                config.parameter_value = value
                config.save()

    return HttpResponseRedirect('/cluster_config/%s'%cluster_id)

@authorize('clusters_rw')
def create_new_cluster(request):
    if request.method == 'POST':
        symbol_id = request.POST['symbolID']
        cluster_type_id = request.POST['clusterTypeID']
        cluster_name = request.POST['clusterName']
        description = request.POST['description']

        if not symbol_id:
            return inform_message('Symbol ID should be not empty!', '/new_cluster')
        if not cluster_type_id:
            return inform_message('Cluster type should be selected!', '/new_cluster')

        if NmCluster.objects.filter(cluster_sid=symbol_id):
            return inform_message('Cluster with SID "%s" is already exists!'%symbol_id, '/new_cluster')

        cluster = NmCluster(cluster_sid=symbol_id, cluster_type=NmClusterType.objects.get(id=cluster_type_id),
                    cluster_name=cluster_name, description=description, last_modifier_id=get_current_user(request).id)
        cluster.save()

        return inform_message('Cluster with SID "%s" is created!'%symbol_id, '/cluster_config/%s'%cluster.id)

    cluster_types = NmClusterType.objects.all()
    return render_to_response('new_cluster.html', {'cluster_types':cluster_types})


@authorize('clusters_rw')
def delete_cluster(request, cluster_id):
    cluster = NmCluster.objects.get(id=cluster_id)

    nodes = NmNode.objects.filter(cluster=cluster)

    if nodes:
        return inform_message('Cluster with SID "%s" contain %s nodes!'%(cluster.cluster_sid, len(nodes)), '/clusters_list')

    config_params = NmConfigSpec.objects.filter(config_object=OT_CLUSTER, object_type_id=cluster.cluster_type.id)
    NmConfig.objects.filter(object_id=cluster.id, parameter__in=config_params).delete()
    symbol_id = cluster.cluster_sid
    cluster.delete()

    return inform_message('Cluster with SID "%s" is deleted!'%symbol_id, '/clusters_list/')


#-----------------------------------------------------------------------------------------------
# --------------------------  Nodes Management  ------------------------------------------------
#-----------------------------------------------------------------------------------------------

#@authorize('nodes_ro')
def get_cluster_nodes(request, cluster_id):
    cluster = NmCluster.objects.get(id=cluster_id)

    nodes = NmNode.objects.filter(cluster=cluster)

    return render_to_response('get_cluster_nodes.html', locals())


class Arch:
    def __init__(self, name):
        self.name = name
        self.is_current_arch = False

@authorize('nodes_ro')
def configure_node(request, node_id):
    node = NmNode.objects.get(id=node_id)

    config_spec = NmConfigSpec.objects.filter(config_object=OT_NODE, object_type_id=node.node_type.id)

    config = []
    cl_name = NmConfigSpec(id='logicalName', parameter_name='Logic name', parameter_type=PT_STRING, posible_values_list='', default_value='')
    cl_name.value = node.logic_name
    cl_name.is_string = True
    config.append(cl_name)

    for spec in config_spec:
        param_value = NmConfig.objects.filter(object_id=node.id, parameter=spec)
        if param_value:
            spec.value = param_value[0].parameter_value
        else:
            spec.value = spec.default_value

        calculate_config_type(spec)
        config.append(spec)

    nodes_types = NmNodeType.objects.all()
    for node_type in nodes_types:
        if node_type == node.node_type:
            node_type.is_current_type = True
    node.nodes_types = nodes_types

    #FIXME: may be Arch should be saved in database!
    node.architectures = [Arch('x86'), Arch('x86_64')]
    for arch in node.architectures:
        if arch.name == node.architecture:
            arch.is_current_arch = True

    return render_to_response('node_config.html', {'node':node, 'config':config})

@authorize('nodes_rw')
def change_node_params(request, node_id):
    if request.method != 'POST':
        raise Exception('POST request expected for change node parameters!')

    cur_user = get_current_user(request)

    for key,value in request.POST.items():
        if key == 'logicalName':
            node = NmNode.objects.get(id=node_id)
            if node.logic_name == value:
                continue
            node.logic_name = value
            node.last_modifier_id = cur_user.id
            node.save()
        else:
            config_spec = NmConfigSpec.objects.get(id=key)
            config = NmConfig.objects.filter(object_id=node_id, parameter=config_spec)
            if not config:
                NmConfig(object_id=node_id, parameter=config_spec, parameter_value=value, last_modifier=cur_user).save()
            else:
                config = config[0]
                if config.parameter_value == value:
                    continue
                config.parameter_value = value
                config.save()

    return HttpResponseRedirect('/configure_node/%s'%node_id)


def reboot_node(hostname, user_name):
   client = DBUSInterfaceClient()

   return client.call_nodes_operation(user_name, [hostname], 'REBOOT', [])

@authorize('nodes_rw')
def change_base_node_params(request, node_id):
    if request.method != 'POST':
        raise Exception('POST request expected for change base node parameters!')
    cur_user = get_current_user(request)
    node = NmNode.objects.get(id=node_id)

    url ='/configure_node/%s'%node_id

    #change hostname
    hostname = request.POST['hostname']
    if not hostname:
        return inform_message('Hostname should be not empty!', url)

    if not re.match('[a-zA-Z][a-zA-Z0-9\-]+$', hostname):
        return inform_message('Hostname is invalid. Allowed characters are: a-z, A-Z, 0-9 and "-"', url)

    old_node_hostname = node.hostname
    if old_node_hostname != hostname:
        node.hostname = hostname

    #change node type
    node_type_id = request.POST['nodeType']
    if not node_type_id:
        raise Exception('Node type id expected in POST message')

    if node.node_type.id != node_type_id:
        node.node_type = NmNodeType.objects.get(id=node_type_id)

    #change architecture
    arch = request.POST['architecture']
    if not arch:
        raise Exception('Node architecture expected in POST message')
    if node.architecture != arch:
        node.architecture = arch

    node.last_modifier_id = cur_user.id
    node.save()

    ret_message = 'Parameters are installed for node!\n'

    if NODES_NAMAGER_SUPPORT:
        #apply parameters
        code,out,err = run_command(['change-node', '--node-type', node.node_type.type_sid, \
                            '--arch', node.architecture, '--hostname', node.hostname, '--uuid', node.node_uuid])
        if code:
            return inform_message('New node parameters saved, but not installed!\nDetails: %s'%err, url)

        #reboot node
        ret_code, msg = reboot_node(old_node_hostname, cur_user.name)
        if ret_code:
            return inform_message('Node is not rebooted! Details: %s'%msg, url)

        ret_message += 'Node rebooting for apply parameters...'

    else:
        ret_message += 'Node is not rebooted because NodesManager is not supported in Console!'

    return inform_message(ret_message, url)

