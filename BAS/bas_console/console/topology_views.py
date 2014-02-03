from base_views import *

def get_nodes_states(request, cluster_id):
    nodes = BasClusterNode.objects.filter(cluster=int(cluster_id))

    results = {}
    for node in nodes:
        iface = NodeInterfaces.get(node.id)

        try:
            ret = iface.service.GetNodeStatistic()
            results[node.id] = True
        except:
            results[node.id] = False

    return HttpResponse(json.dumps(results), mimetype="application/json")


#---------TOPOLOGY_READ------------------------

@authorize(TOPOLOGY_READ, save_path=True)
def clusters_list(request):
    menuitem = TOPOLOGY_MENU

    clusters = BasCluster.objects.all()


    for cluster in clusters:
        nodes = BasClusterNode.objects.filter(cluster=cluster)
        cluster.nodes_count = len(nodes)

    return render_to_response('clusters.html',{'menuitem':menuitem, 'clusters': clusters})

@authorize(TOPOLOGY_READ, save_path=True)
def cluster_index(request, cluster_id):
    menuitem = TOPOLOGY_MENU

    nodes = BasClusterNode.objects.filter(cluster=cluster_id).order_by('id')

    system_settings = BasConfig.objects.filter(config_type=1, config_object_id=cluster_id ).order_by('id')

    request.session['cluster_id'] = cluster_id

    return render_to_response('cluster_nodes.html',{'menuitem':menuitem, 'nodes': nodes, 'system_settings':system_settings, 'cluster_id':cluster_id})


@authorize(TOPOLOGY_READ, save_path=True)
def get_node(request, node_id):
    node = BasClusterNode.objects.get(id=node_id)

    class Parameter:
        def __init__(self, name, value):
            self.name = name
            self.value = value

    node.parameters = []


    iface = NodeInterfaces.get(node_id)

    var = iface.factory.create('RequestGetNodeStatistic')
    var.auth.login = BAS_NODE_LOGIN
    var.auth.password = BAS_NODE_PASSWORD

    try:
        ret = iface.service.GetNodeStatistic(var)
    except:
        node.parameters.append(Parameter('State', 'Down'))
    else:
        if ret.ret_code != 0:
            return inform_message(request, "Error! Node data is not received! \nDescription: %s"%ret.ret_message)

        node.parameters.append(Parameter('State', 'Up'))
        node.parameters.append(Parameter('Uptime',ret.statistic.uptime.split('.')[0]))
        node.parameters.append(Parameter('Threads count', ret.statistic.threads))
        node.parameters.append(Parameter('Load avarage (5 min)', ret.statistic.loadavg_5))
        node.parameters.append(Parameter('Load avarage (10 min)', ret.statistic.loadavg_10))
        node.parameters.append(Parameter('Load avarage (15 min)', ret.statistic.loadavg_15))
        node.parameters.append(Parameter('System time', ret.statistic.stime + ' sec'))
        node.parameters.append(Parameter('User time', ret.statistic.utime + ' sec'))
        node.parameters.append(Parameter('Allocated memory',  '%.1f MB' % (int(ret.statistic.memory)/1024.0)))


    return render_to_response('node_info.html',{ 'menuitem':1, 'node':node, 'cluster_id': node.cluster_id})


'''

@authorize(APP_READ, save_path=True)
def get_applications_log(request, page_num):
    application_id = request.session['application_id']
    application = BasApplication.objects.get(id=application_id)
    same_named_apps = BasApplication.objects.filter(cluster=application.cluster.id, app_name=application.app_name)
    min_d = None
    from_dt = to_dt = None

    if request.method == 'POST':
        from_dt = date(int(request.POST['fromYear']), int(request.POST['fromMonth']), int(request.POST['fromDay']))
        to_dt = date(int(request.POST['toYear']), int(request.POST['toMonth']), int(request.POST['toDay']))

        request.session['from_date'] = from_dt
        request.session['to_date'] = to_dt
    else:
        if page_num == '':
            from_dt = request.session['from_date'] = date.today()
            to_dt = request.session['to_date'] = date.today()
        else:
            from_dt = request.session.get('from_date', date.today())
            to_dt = request.session.get('to_date', date.today())

    #find last stat record
    min_d = BasAppMessage.objects.aggregate(Min("datetime"))['datetime__min']
    if not min_d:
        min_d = date.today()

    from_cal = Calendar(from_dt, min_d)
    to_cal = Calendar(to_dt, min_d)

    if not page_num:
        num = 0
    else:
        num = int(page_num)
    page = 15

    methods = BasAppMethod.objects.filter(application__in=same_named_apps)
    logs = BasAppMessage.objects.filter(method__in = methods, datetime__gte=from_dt,
        datetime__lt=(to_dt+timedelta(1))).order_by("-datetime")[num*page:(num+1)*page]

    if len(logs) != page:
        islastpage = 1
    else:
        islastpage = 0

    return render_to_response('applications_logs.html',{'logs':logs, 'islastpage':islastpage, 'page_num':num,'menuitem':2, 'application':application, 'calendar_from':from_cal, 'calendar_to':to_cal})
'''

@authorize(TOPOLOGY_READ, save_path=True)
def get_server_log(request, page_num):
    class LogLevel:
        def __init__(self, id, name):
            self.id = id
            self.name = name

    cluster_id = request.session['cluster_id']
    node = int(request.session.get('node_id',-1))
    level = int(request.session.get('level_id',-1))
    min_d = None
    from_dt = to_dt = None

    if not page_num:
        num = 0
    else:
        num = int(page_num)
    page = 15

    if request.method == 'POST':
        level = int(request.POST['levels_list'])
        node = int(request.POST['nodes_list'])
        from_dt = date(int(request.POST['fromYear']), int(request.POST['fromMonth']), int(request.POST['fromDay']))
        to_dt = date(int(request.POST['toYear']), int(request.POST['toMonth']), int(request.POST['toDay']))

        request.session['from_date'] = from_dt
        request.session['to_date'] = to_dt
    else:
        if page_num == '':
            from_dt = request.session['from_date'] = date.today()
            to_dt = request.session['to_date'] = date.today()
        else:
            from_dt = request.session.get('from_date', date.today())
            to_dt = request.session.get('to_date', date.today())

    #find last stat record
    min_d = BasLog.objects.aggregate(Min("msg_datetime"))['msg_datetime__min']
    if not min_d:
        min_d = date.today()

    from_cal = Calendar(from_dt, min_d)
    to_cal = Calendar(to_dt, min_d)

    if node > 0 and level > 0:
        logs = BasLog.objects.filter(node=node, msg_level=level)
    elif node > 0 and level < 0:
        logs = BasLog.objects.filter(node=node)
    elif node < 0 and level >= 0:
        logs = BasLog.objects.filter(msg_level=level)
    else:
        logs = BasLog.objects

    logs = logs.filter(msg_datetime__gte=from_dt, msg_datetime__lt=(to_dt+timedelta(1))).order_by("-msg_datetime")[num*page:(num+1)*page]

    nodes = BasClusterNode.objects.filter(cluster=cluster_id)
    ret_nodes = [BasClusterNode(id=-1, logic_name='All nodes')]
    for curnode in nodes:
        if curnode.id == node:
            ret_nodes.insert(0, curnode)
        else:
            ret_nodes.append(curnode)

    levels = [LogLevel(-1,'All levels'),LogLevel(0,'Information'),LogLevel(4,'Warning'),LogLevel(2,'Error')]
    ret_levels = []
    for curlevel in levels:
        if curlevel.id == level:
            ret_levels.insert(0, curlevel)
        else:
            ret_levels.append(curlevel)

    if len(logs) != page:
        islastpage = 1
    else:
        islastpage = 0

    request.session['node_id'] = node
    request.session['level_id'] = level
    return render_to_response('server_logs.html',{'logs':logs, 'islastpage':islastpage, 'page_num':num,'menuitem':1, 'cluster_id':cluster_id,'nodes':ret_nodes, 'levels':ret_levels, 'calendar_from':from_cal,'calendar_to':to_cal})



#---------TOPOLOGY_MODIFY------------------------


@authorize(TOPOLOGY_MODIFY)
@transaction.commit_manually
def modify_cluster(request, cluster_id):
    if cluster_id:
        cluster = BasCluster.objects.get(id=cluster_id)
    else:
        #append new cluster
        cluster = BasCluster(cluster_name='', cluster_sid='')


    if request.method == 'POST':
        def new_config(param_name, param_type, param_value, descr):
            BasConfig(config_type=1, config_object_id=cluster.id, \
                    param_name=param_name, param_type=param_type, \
                    param_value=param_value,description=descr).save()

        form = ModifyClusterForm(request.POST)
        form.set_clusterid(cluster_id)
        if form.is_valid():
            cd = form.cleaned_data

            if cluster.cluster_name == cd['cluster_name'] and cluster.cluster_sid == cd['cluster_sid']:
                return HttpResponseRedirect('/clusters')
            else:
                cluster.cluster_name = cd['cluster_name']
                cluster.cluster_sid = cd['cluster_sid']

                try:
                    cluster.save()

                    if not cluster_id:
                        #FIXME: make service CreateNewCluster at BAS and call it
                        new_config('max_threads', 2, '20', 'Maximum work threads count')
                        new_config('real_hostname', 1, 'change.me', 'Hostname of load balancer')
                        new_config('http_port', 2, '8080', 'HTTP listen port')
                        new_config('ssl_port', 2, '443', 'HTTPS listen port')
                        new_config('log_write_timeout', 2, '5', 'Statistic logs write timeout')
                        new_config('system_transport', 1, 'HTTP', 'Transport of BAS system services')
                except Exception, err:
                    transaction.rollback()
                    raise err
                else:
                    transaction.commit()

                return inform_message(request, 'Cluster information is saved!')
    else:
        form = ModifyClusterForm({'cluster_name':cluster.cluster_name,'cluster_sid':cluster.cluster_sid})
        form.set_clusterid(cluster_id)

    return render_to_response('modify_form.html',{'form':form, 'cancel_href':'/clusters'})



@authorize(TOPOLOGY_MODIFY)
def modify_node(request, node_id):
    cluster_id = int(request.session['cluster_id'])
    cluster_link = '/cluster_%i'%cluster_id

    if node_id:
        node = BasClusterNode.objects.get(id=node_id)
    else:
        #append new node
        node = BasClusterNode(hostname='', logic_name='', cluster_id=cluster_id, datestart=datetime.now())


    if request.method == 'POST':
        form = ModifyNodeForm(request.POST)
        form.set_nodeid(node_id)
        if form.is_valid():
            cd = form.cleaned_data

            if node.logic_name == cd['logic_name'] and node.hostname == cd['host']:
                return HttpResponseRedirect(cluster_link)
            else:
                node.logic_name = cd['logic_name']
                node.hostname = cd['host']
                node.save()

                NodeInterfaces.setup()
                return inform_message(request, 'Node information is saved!')
    else:
        form = ModifyNodeForm({'logic_name':node.logic_name,'host':node.hostname})
        form.set_nodeid(node_id)

    return render_to_response('modify_form.html',{'form':form, 'cancel_href':cluster_link})

@authorize(TOPOLOGY_MODIFY)
@transaction.commit_manually
def remote_cluster(request, cluster_id):
    cluster = BasCluster.objects.get(id=cluster_id)

    nodes = len(BasClusterNode.objects.filter(cluster=cluster))

    if nodes > 0:
        return inform_message(request, "Cluster '%s' has execution nodes! Remove this nodes before removing cluster"%cluster.cluster_sid)

    try:
        configs = BasConfig.objects.filter(config_type=1, config_object_id=cluster.id)
        for config in configs:
            config.delete()
        cluster.delete()
    except Exception, err:
        transaction.rollback()
        raise err
    else:
        transaction.commit()

    return inform_message(request, "Cluster '%s' is removed!"%cluster.cluster_sid)


@authorize(TOPOLOGY_MODIFY)
def remote_node(request, node_id):
    node = BasClusterNode.objects.get(id=node_id)
    logic_name = node.logic_name

    node.delete()

    NodeInterfaces.setup()

    return inform_message(request, "Node '%s' is removed!"%logic_name)



#---------TOPOLOGY_ADMIN------------------------


@authorize(TOPOLOGY_ADMIN)
def reload_cluster(request, cluster_id):
    nodes = BasClusterNode.objects.filter(cluster=cluster_id)

    for node in nodes:
        try:
            iface = NodeInterfaces.get(node.id)
            inVar = iface.factory.create('RequestRestartServerNode')
            inVar.auth.login = BAS_NODE_LOGIN
            inVar.auth.password = BAS_NODE_PASSWORD

            iface.service.RestartServerNode(inVar)
        except Exception, err:
            pass
        
    NodeInterfaces.setup()

    return inform_message(request, "Cluster's nodes are restarting! See server log for details... ")


def check_system_setting(key, value):
    key = str(key)
    value = str(value)

    if key.endswith('_port'):
        try:
            value = int(value)
            if value < 0 or value > 65535:
                raise Exception()
        except:
            return 'Port value must be integer value (0..65535)'

    elif key.endswith('_timeout'):
        try:
            value = int(value)
            if value < 0:
                raise Exception()
        except:
            return 'Timeout value must be integer'

    elif key.endswith('_threads'):
        try:
            value = int(value)
            if value < 0:
                raise Exception()
        except:
            return 'Thread count value must be integer'


    elif key == 'system_transport':
        if value.lower() not in ['http','https']:
            return 'System transport must be HTTP or HTTPS'


@authorize(TOPOLOGY_ADMIN)
def save_system_settings(request):
    updates = []
    cluster_id = request.session.get('cluster_id',None)

    if not cluster_id:
        return HttpResponseRedirect('/clusters/')

    if request.method == 'POST':
        settings = BasConfig.objects.filter(config_type=1, config_object_id=cluster_id)

        for key in request.POST.keys():
            for setting in settings:
                if setting.param_name == key:
                    value = request.POST.get(key)

                    error = check_system_setting(key, value)
                    if error:
                        return inform_message(request, 'ERROR: %s'%error)

                    if setting.param_value != value:
                        setting.param_value = value
                        updates.append(setting)
                    break

        for update in updates:
            update.save()

    else:
        print "NOT POST method"

    if not len(updates):
        return HttpResponseRedirect('/cluster_%s'%cluster_id)

    return inform_message(request, 'Newer server settings saved! Reload all nodes in cluster for apply this settings')

