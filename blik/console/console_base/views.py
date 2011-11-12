from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.db import connection, transaction
from console_base.menu import get_menu
from console_base.auth import get_current_user, authorize, is_authorize, cache_users, is_authenticated
from console_base.models import *
from console_base.library import *
from copy import copy
import json
import re
import hashlib

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

@authorize('nodes_ro')
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

    #FIXME: Arch should be saved in database!
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

def synchronize_node(hostname, user_name):
   client = DBUSInterfaceClient()

   return client.call_nodes_operation(user_name, [hostname], 'SYNC', [])


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

    #set optional parameters (used for node registration)
    if request.POST.has_key('clusterId'):
        cluster = NmCluster.objects.get(id=request.POST['clusterId'])
        node.cluster = cluster

    if request.POST.has_key('logicName'):
        node.logic_name = request.POST['logicName']

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


@authorize('nodes_rw')
def delete_node(request, node_id):
    node = NmNode.objects.get(id=node_id)

    config_params = NmConfigSpec.objects.filter(config_object=OT_NODE, object_type_id=node.node_type.id)
    NmConfig.objects.filter(object_id=node.id, parameter__in=config_params).delete()
    hostname = node.hostname
    if node.cluster:
        url = '/cluster_nodes/%s'%node.cluster.id
    else:
        url = '/unregistered_nodes'

    node.delete()

    return inform_message('Node with hostname "%s" is deleted from database!'%hostname, url)


@authorize('nodes_rw')
def reboot_node(request, node_id):
    node = NmNode.objects.get(id=node_id)
    url = '/cluster_nodes/%s'%node.cluster.id

    if NODES_NAMAGER_SUPPORT:
        cur_user = get_current_user(request)

        #reboot node
        ret_code, msg = reboot_node(node.hostname, cur_user.name)
        if ret_code:
            return inform_message('Node is not rebooted! Details: %s'%msg, url)

    else:
        return inform_message('Node is not rebooted because NodesManager is not supported in Console!', url)

    return inform_message('Node is rebooting now!', url)

@authorize('nodes_rw')
def sync_node(request, node_id):
    node = NmNode.objects.get(id=node_id)
    url = '/cluster_nodes/%s'%node.cluster.id

    if NODES_NAMAGER_SUPPORT:
        cur_user = get_current_user(request)

        #synchronize node
        ret_code, msg = synchronize_node(node.hostname, cur_user.name)
        if ret_code:
            return inform_message('Node is not synchronized! Details: %s'%msg, url)

    else:
        return inform_message('Node is not synchronized because NodesManager is not supported in Console!', url)

    return inform_message('Node parameters are synchronized!', url)


@authorize('nodes_ro')
def unregistered_nodes(request):
    nodes = NmNode.objects.filter(admin_status=NEW_NODE)
    return render_to_response('unregistered_nodes.html', {'nodes':nodes})


@authorize('nodes_rw')
def register_node(request, node_id):
    node = NmNode.objects.get(id=node_id)

    if node.admin_status != NEW_NODE:
        return inform_message('Node with hostname %s is already registered!'%node.hostname, '/unregistered_nodes')

    node.nodes_types = NmNodeType.objects.all()

    #FIXME: Arch should be saved in database!
    node.architectures = [Arch('x86'), Arch('x86_64')]

    node.all_clusters = NmCluster.objects.all()

    return render_to_response('register_node.html', {'node':node})


#-----------------------------------------------------------------------------------------------
# ---------------------------  Logs Management  ------------------------------------------------
#-----------------------------------------------------------------------------------------------


@authorize('operlogs_viewer')
def get_operations_logs(request, cluster_id):
    cluster = NmCluster.objects.get(id=cluster_id)
    nodes = NmNode.objects.filter(cluster=cluster)
    operations = NmOperation.objects.all()

    return render_to_response('operations_logs.html', locals())

@authorize('operlogs_viewer')
def get_operlog_data(request):
    if request.method != 'POST':
        raise Exception('get_operlog_data expect POST request')

    data = request.POST
    sortfield = data['sortname']
    sortorder = data['sortorder']
    cluster_id = data['cluster_id']
    operation_id = data.get('operation','')
    node_id = data.get('node','')
    oper_status = data.get('oper_status', '')
    start_dt = data.get('start_dt','')
    end_dt = data.get('end_dt','')
    page = int(data['page'])
    rows_count = int(data['rp'])


    data_header = """
    SELECT inst.id, oper.name, inst.status, inst.start_datetime,
        (SELECT ret_message FROM nm_operation_progress WHERE instance_id=inst.id ORDER BY end_datetime DESC LIMIT 1) last_response
    """
    count_header = "SELECT count (*) "
    base_query = """
    FROM nm_operation_instance inst, nm_operation_progress prog, nm_operation oper
    WHERE inst.operation_id = oper.id
        AND prog.instance_id = inst.id
        AND prog.node_id IN (SELECT id FROM nm_node WHERE cluster_id=%s)
    """

    params = [cluster_id]
    if operation_id:
        base_query += ' AND inst.operation_id = %s'
        params.append(operation_id)
    if node_id:
        base_query += ' AND prog.node_id = %s'
        params.append(node_id)
    if oper_status:
        base_query += ' AND inst.status = %s'
        params.append(oper_status)
    if start_dt:
        base_query += ' AND inst.start_datetime >= %s'
        params.append(start_dt)
    if end_dt:
        base_query += ' AND inst.end_datetime <= %s'
        params.append(end_dt)

    cursor = connection.cursor()
    cursor.execute(count_header+base_query, params)
    count = cursor.fetchone()[0]

    if sortfield != 'undefined':
        base_query += ' ORDER BY inst.%s %s'%(sortfield, sortorder)

    base_query += ' OFFSET %s LIMIT %s'
    params.append((page-1)*rows_count)
    params.append(rows_count)

    cursor = connection.cursor()
    cursor.execute(data_header+base_query, params)
    rows = cursor.fetchall()

    ret_list = []
    for i,row in enumerate(rows):
        ret = dict()
        ret['id'] = i
        ret['cell'] = (row[0], row[1], OPER_STATUS_MAP[int(row[2])], str(row[3]), row[4])

        ret_list.append(ret)

    ret_map = dict()
    ret_map['page'] = page
    ret_map['total'] = count
    ret_map['rows'] = ret_list

    return HttpResponse(json.dumps(ret_map), mimetype="application/json")


@authorize('syslogs_viewer')
def get_system_logs(request, cluster_id):
    cluster = NmCluster.objects.get(id=cluster_id)
    nodes = NmNode.objects.filter(cluster=cluster)

    return render_to_response('system_logs.html', locals())

@authorize('syslogs_viewer')
def get_syslog_data(request):
    if request.method != 'POST':
        raise Exception('get_operlog_data expect POST request')

    data = request.POST
    sortfield = data['sortname']
    sortorder = data['sortorder']
    cluster_id = data['cluster_id']
    node_id = data.get('node','')
    facility = data.get('facility', '').strip()
    priority = data.get('priority','').strip()
    level = data.get('level','').strip()
    program = data.get('program','').strip()
    message = data.get('message','').strip()
    start_dt = data.get('start_dt','')
    end_dt = data.get('end_dt','')
    page = int(data['page'])
    rows_count = int(data['rp'])

    nodes = NmNode.objects.filter(cluster=cluster_id)
    syslog_data = SystemLog.objects.filter(node_id__in=nodes)

    if node_id:
        syslog_data = syslog_data.filter(node_id=node_id)
    if facility:
        syslog_data = syslog_data.filter(facility=facility)
    if priority:
        syslog_data = syslog_data.filter(priority=priority)
    if level:
        syslog_data = syslog_data.filter(level=level)
    if program:
        syslog_data = syslog_data.filter(program=program)
    if start_dt:
        syslog_data = syslog_data.filter(log_timestamp__gte=start_dt)
    if end_dt:
        syslog_data = syslog_data.filter(log_timestamp__lt=end_dt)
    if message:
        syslog_data = syslog_data.filter(msg__contains= message )

    if sortfield and sortfield != 'undefined':
        if sortorder == 'desk':
            sortfield == '-%s'%sortfield

        syslog_data = syslog_data.order_by(sortfield)

    count = len(syslog_data)
    syslog_data = syslog_data[rows_count*(page-1) : rows_count*page]

    ret_list = []
    for i,row in enumerate(syslog_data):
        ret = dict()
        ret['id'] = i
        ret['cell'] = (row.id, row.log_timestamp, NmNode.objects.get(id=row.node_id).hostname, row.facility, row.priority, row.level, row.tag, row.program, row.msg)

        ret_list.append(ret)

    ret_map = dict()
    ret_map['page'] = page
    ret_map['total'] = count
    ret_map['rows'] = ret_list

    return HttpResponse(json.dumps(ret_map), mimetype="application/json")


#-----------------------------------------------------------------------------------------------
# ---------------------------  Users Management  -----------------------------------------------
#-----------------------------------------------------------------------------------------------

def get_users_list(request):
    users = NmUser.objects.all()
    return render_to_response('users_list.html', locals())


def validate_email(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return 1
    return 0

#@authorize('users_admin')
def create_new_user(request):
    if request.method == 'POST':
        #check username
        user_name = request.POST['user_name'].strip()
        if not user_name:
            return inform_message('User name should be not empty!', '/create_new_user')
        if NmUser.objects.filter(name=user_name):
            return inform_message('User with login "%s" is already exists in database!\nPlease, select another user login', '/create_new_user')

        #check password
        password = request.POST['password'].strip()
        re_password = request.POST['re_password'].strip()
        if not password:
            return inform_message('Password should be not empty!', '/create_new_user')
        if password != re_password:
            return inform_message('Typed passwords are not equal!', '/create_new_user')
        md5 = hashlib.md5()
        md5.update(password.encode('utf8'))
        passwd = md5.hexdigest()

        #check email
        email = request.POST['email'].strip()
        if email and not validate_email(email):
            return inform_message('Email address "%s" is not valid!'%email, '/create_new_user')
        add_info = request.POST['addinfo']

        user = NmUser(name=user_name, password_hash=passwd, email_address=email, additional_info=add_info)
        user.save()

        cache_users()

        return inform_message('User with login "%s" is created!'%user_name, '/edit_user_roles/%s'%user.id)

    return render_to_response('new_user.html', locals())


def edit_user(request, user_id):
    if not is_authenticated(request):
        return HttpResponseRedirect('/auth')

    is_auth = is_authorize(request, 'users_admin')
    if not is_auth and (get_current_user(request).id != int(user_id)):
        return inform_message('Your permissions allows you change only your account!', '/users_list')

    user = NmUser.objects.get(id=user_id)

    if request.method == 'POST':
        password = request.POST['password'].strip()
        re_password = request.POST['re_password'].strip()
        if password and password != re_password:
            return inform_message('Typed passwords are not equal!', '/edit_user/%s'%user.id)
        if password:
            md5 = hashlib.md5()
            md5.update(password.encode('utf8'))
            passwd = md5.hexdigest()
            user.password_hash = passwd

        #check email
        email = request.POST['email'].strip()
        if email and not validate_email(email):
            return inform_message('Email address "%s" is not valid!'%email, '/edit_user/%s'%user.id)

        user.email_address = email
        user.additional_info = request.POST['addinfo']
        user.save()
        return inform_message('User with login "%s" is updated!'%user.name, '/users_list')

    return render_to_response('edit_user.html', locals())


@authorize('users_admin')
def edit_user_roles(request, user_id):
    user = NmUser.objects.get(id=user_id)

    if request.method == 'POST':
        method = request.POST['method'].strip()
        value = request.POST['value'].strip()

        role = NmRole.objects.get(id=value)

        if method == 'push':
            #bind role to user (if already not binded)
            if not NmUserRole.objects.filter(user=user, role=role):
                NmUserRole(user=user, role=role).save()
        elif method == 'pop':
            #unbind role from user 
            if role.role_sid != 'users_admin':
                NmUserRole.objects.filter(user=user, role=role).delete()
        else:
            raise Exception('Edit user roles method "%s" is not valid!'%method)

        cache_users()
        return HttpResponse('ok')

    all_roles = NmRole.objects.all()
    user_roles = NmUserRole.objects.filter(user=int(user_id))

    return render_to_response('edit_user_roles.html', locals())

@authorize('users_admin')
def delete_user(request, user_id):
    if int(user_id) == get_current_user(request).id:
        return inform_message('You can not delete itself!', '/users_list')

    NmUserRole.objects.filter(user=int(user_id)).delete()
    user = NmUser.objects.get(id=user_id)
    user_name = user.name
    user.delete()

    cache_users()

    return inform_message('User with login "%s" is deleted!'%user_name, '/users_list')
