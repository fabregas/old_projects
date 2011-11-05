from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from console_base.menu import get_menu
from console_base.auth import get_current_user, authorize
from console_base.models import *
from console_base.library import *
from copy import copy
import json

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


