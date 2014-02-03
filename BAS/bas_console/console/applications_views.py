
from base_views import *
import base64



def get_system_service(inVariableName, cluster_id):
    client = Client(SYSTEM_SERVICE_WSDL)
    conf = BasConfig.objects.get(config_type=1, config_object_id=int(cluster_id), param_name='real_hostname')

    client = make_client_endpoint(client, conf.param_value, 'System', int(cluster_id))

    inputVar = client.factory.create(inVariableName)

    inputVar.auth.login = BAS_NODE_LOGIN
    inputVar.auth.password = BAS_NODE_PASSWORD

    return client, inputVar


def get_application_state(request, application_id):
    cluster_id = request.session['cluster_id']
    client, inputVar = get_system_service('RequestGetApplicationState', cluster_id)

    if application_id:
        applications = [BasApplication.objects.get(id=application_id)]
    else:
        applications = BasApplication.objects.filter(cluster=cluster_id, active_flag=1, app_type="native_app")


    results = {}
    for application in applications:
        results[application.id] = False
        
    for application in applications:
        inputVar.application_id = application.id

        try:
            ret = client.service.GetApplicationState(inputVar)
        except:
            break
        else:
            if str(ret.state) == 'up':
                results[application.id] = True
    
    return HttpResponse(json.dumps(results), mimetype="application/json")


#---------APP_READ------------------------

@authorize(APP_READ, save_path=True)
def get_applications(request, cluster_id):
    menuitem = APPLICATIONS_MENU

    clusters = BasCluster.objects.all()
    if not clusters:
        return inform_message(request, "No applications found in database")

    ret_clusters = []

    if not cluster_id:
        cluster_id = request.session.get('cluster_id', clusters[0].id)

    for cluster in clusters:
        if int(cluster.id) == int(cluster_id):
            ret_clusters.insert(0, cluster)
        else:
            ret_clusters.append(cluster)

    applications = BasApplication.objects.filter(cluster=ret_clusters[0],active_flag=1).order_by('app_type','app_name')

    for i,app in enumerate(applications):
        app.num = i+1
        if str(app.app_type) == 'native_app':
            app.is_native = True

    request.session['cluster_id'] = ret_clusters[0].id

    settings = BasConfig.objects.filter(config_type=2, config_object_id=cluster_id ).order_by('id')

    return render_to_response('applications.html',{'menuitem':menuitem, 'clusters':ret_clusters, 'applications':applications,'settings':settings})


@authorize(APP_READ, save_path=True)
def application_index(request, application_id):
    menuitem = APPLICATIONS_MENU
    application_id = int(application_id)

    methods = BasAppMethod.objects.filter(application=application_id).order_by("method_id")
    for i, method in enumerate(methods):
        method.num = i+1

    settings = BasConfig.objects.filter(config_type=3, config_object_id=application_id ).order_by('id')

    application = BasApplication.objects.get(id=application_id)

    client, inputVar = get_system_service('RequestGetApplicationState', application.cluster.id)
    inputVar.application_id = application.id
    application.state = False
    try:
        ret = client.service.GetApplicationState(inputVar)
    except:
        pass
    else:
        if str(ret.state) == 'up':
            application.state = True

    old_applications = BasApplication.objects.filter(active_flag=0, app_name=application.app_name).order_by('-deploy_datetime')

    request.session['application_id'] = application_id

    return render_to_response('application.html',{'menuitem':menuitem, 'methods':methods, 'settings':settings, 'application':application, 'old_applications':old_applications})



@authorize(APP_READ, save_path=True)
def sharedlibrary_index(request, lib_id):
    menuitem = APPLICATIONS_MENU
    lib_id = int(lib_id)

    library = BasApplication.objects.get(id=lib_id)
    library.state = True

    old_libs = BasApplication.objects.filter(active_flag=0, app_name=library.app_name).order_by('-deploy_datetime')

    request.session['application_id'] = lib_id

    return render_to_response('sharedlibrary.html',{'menuitem':menuitem, 'application':library, 'old_applications':old_libs})


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


@authorize(APP_READ, save_path=True)
def get_log_message(request, log_id):
    application_id = request.session['application_id']
    application = BasApplication.objects.get(id=application_id)
    log = BasAppMessage.objects.filter(id=log_id)[0]

    return render_to_response('log_message.html',{'log':log, 'menuitem':2, 'application':application})


@authorize(APP_READ, save_path=True)
def get_application_statistic(request):
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
        from_dt = request.session['from_date'] = date.today()
        to_dt = request.session['to_date'] = date.today()

    #find last stat record
    min_d = BasAppStatistic.objects.aggregate(Min("write_datetime"))['write_datetime__min']
    if not min_d:
        min_d = date.today()

    from_cal = Calendar(from_dt, min_d)
    to_cal = Calendar(to_dt, min_d)

    statistic = BasAppStatistic.objects.filter(app__in=same_named_apps,
            write_datetime__gte=from_dt, write_datetime__lt=(to_dt+timedelta(1))).values('node_id').annotate(
                in_count=Sum('in_count'),out_count=Sum('out_count'),err_count=Sum('err_count'))

    all = BasAppStatistic(in_count=0,out_count=0,err_count=0)
    for item in statistic:
        all.in_count += item['in_count']
        all.out_count += item['out_count']
        all.err_count += item['err_count']

        item['node'] = BasClusterNode.objects.get(id=item['node_id'])
        

    return render_to_response('application_statistic.html',{'statistic':statistic, 'menuitem':2, 'application':application, 'calendar_from':from_cal, 'calendar_to':to_cal, 'all':all})



#---------APP_ADMIN------------------------


def modify_config_param(request, param_id, conf, cancel_href):
    if request.method == 'POST':
        form = ModifyConfigForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            if conf.param_name == cd['param_name'] and int(conf.param_type) == int(cd['param_type']) and conf.param_value == cd['param_value'] and conf.description == cd['description']:
                return HttpResponseRedirect('/applications')
            else:
                for key in cd:
                    cd[key] = cd[key].strip()

                conf.param_name = cd['param_name']
                conf.param_type = cd['param_type']
                conf.param_value = cd['param_value']
                conf.description = cd['description']
                conf.save()

                return inform_message(request, 'Parameter information is saved!')
    else:
        form = ModifyConfigForm({'param_name':conf.param_name,'param_type':conf.param_type, 'param_value':conf.param_value, 'description':conf.description})

    if param_id:
        remlink = '/removeparam/%s'%param_id
    else:
        remlink = None
    return render_to_response('modify_form.html',{'form':form, 'cancel_href':cancel_href, 'delete_href':remlink})


@authorize(APP_ADMIN)
def modify_global_app_param(request, param_id):
    if param_id:
        conf = BasConfig.objects.get(id = param_id)
    else:
        cluster_id = int(request.session['cluster_id'])
        conf = BasConfig(config_type=2, config_object_id=cluster_id, param_name='',param_type=1, param_value='',description='')

    return modify_config_param(request, param_id, conf, '/applications')


@authorize(APP_ADMIN)
def remove_config_param(request, param_id):
    conf = BasConfig.objects.get(id = param_id)

    param_name = conf.param_name

    conf.delete()

    return inform_message(request, "Configuration parameter '%s' is removed!"%param_name)

@authorize(APP_ADMIN)
def modify_local_app_param(request, param_id):
    app_id = int(request.session['application_id'])
    if param_id:
        conf = BasConfig.objects.get(id = param_id)
    else:
        conf = BasConfig(config_type=3, config_object_id=app_id, param_name='',param_type=1, param_value='',description='')

    return modify_config_param(request, param_id, conf, '/application/%i'%app_id)



@authorize(APP_ADMIN)
def start_application(request, application_id):
    application = BasApplication.objects.get(id=application_id)

    client, inputVar = get_system_service('RequestStartApplication', application.cluster.id)
    inputVar.application_id = application.id

    try:
        ret = client.service.StartApplication(inputVar)
    except Exception, err:
        return inform_message(request, "Error! %s"%err)


    if int(ret.ret_code) != 0:
        return inform_message(request, "Warning! %s"%(ret.ret_message))

    return inform_message(request, "Application %s is successfully started!"%application.app_name)


@authorize(APP_ADMIN)
def restart_application(request, application_id):
    application = BasApplication.objects.get(id=application_id)

    client, inputVar = get_system_service('RequestRestartApplication',application.cluster.id)
    inputVar.application_id = application.id

    try:
        ret = client.service.RestartApplication(inputVar)
    except Exception, err:
        return inform_message(request, "Error! %s"%err)

    if int(ret.ret_code) != 0:
        return inform_message(request, "Warning! %s"%(ret.ret_message))

    return inform_message(request, "Application %s is successfully restarted!"%application.app_name)



@authorize(APP_ADMIN)
def stop_application(request, application_id):
    application = BasApplication.objects.get(id=application_id)

    client, inputVar = get_system_service('RequestStopApplication', application.cluster.id)
    inputVar.application_id = application.id

    try:
        ret = client.service.StopApplication(inputVar)
    except Exception, err:
        return inform_message(request, "Error! %s"%err)

    if int(ret.ret_code) != 0:
        return inform_message(request, "Warning! %s"%(ret.ret_message))

    return inform_message(request, "Application %s is successfully stoped!"%application.app_name)


@authorize(APP_ADMIN)
def clear_statistic(request):
    application_id = request.session['application_id']
    application = BasApplication.objects.get(id=application_id)
    same_named_apps = BasApplication.objects.filter(cluster=application.cluster.id, app_name=application.app_name)

    from_dt = request.session['from_date']
    to_dt = request.session['to_date']

    statistic = BasAppStatistic.objects.filter(app__in=same_named_apps,
        write_datetime__gte=from_dt, write_datetime__lt=(to_dt+timedelta(1))).delete()

    return inform_message(request, "Statistic are cleared!")

@authorize(APP_ADMIN)
def clear_messages(request):
    application_id = request.session['application_id']
    application = BasApplication.objects.get(id=application_id)
    same_named_apps = BasApplication.objects.filter(cluster=application.cluster.id, app_name=application.app_name)

    from_dt = request.session['from_date']
    to_dt = request.session['to_date']

    methods = BasAppMethod.objects.filter(application__in=same_named_apps)
    logs = BasAppMessage.objects.filter(method__in = methods,
        datetime__gte=from_dt, datetime__lt=(to_dt+timedelta(1))).delete()

    return inform_message(request, "Messages are cleared!")

@authorize(APP_ADMIN)
def save_method_logging(request):
    if request.method == 'POST':
        application_id = request.session['application_id']
        methods = BasAppMethod.objects.filter(application=application_id)

        data = request.POST

        for method in methods:
            in_l = int(data.has_key('input_%s' % method.method_name)) << 1
            out_l = int(data.has_key('output_%s' % method.method_name)) << 2

            method.status = in_l | out_l
            method.save()
    else:
        raise Exception('POST method expected!')

    return HttpResponseRedirect('/application/%s'%application_id)


@authorize(APP_ADMIN)
def test_application_method(request, method_id):
    method = BasAppMethod.objects.get(method_id=int(method_id))

    def init_variable(var):
        isSet = False

        if type(var) == list:
            return '' #TODO: implement list element descriptions

        for param in dir(var):
            if not param.startswith('__'):
                seted = init_variable(getattr(var,param))
                if seted:
                    continue

                setattr(var, param, '???')
                isSet = True
        return isSet


    http_port = BasConfig.objects.get(config_type=1, config_object_id=method.application.cluster_id, param_name='http_port')
    hostname = BasConfig.objects.get(config_type=1, config_object_id=method.application.cluster_id, param_name='real_hostname')

    try:
        client = Client("http://%s:%s/%s/.wsdl" % (hostname.param_value, http_port.param_value, method.application.app_name))
    except Exception, err:
            return inform_message(request, "Error! Can't parse application WSDL! Details: %s"%err)

    if request.method == 'POST':
        inMessageEnvelop = str(request.POST['inputMessage'])

        try:
            mtd = getattr(client.service[method.application.app_name], method.method_name)

            ret = mtd(__inject={'msg':str(inMessageEnvelop)})
        except Exception, err:
            return inform_message(request, "Error! Details: %s"%err)

        return render_to_response('method_test_result.html',{'message':ret, 'redirect_link':'/application/%s'%method.application.id})


    try:
        method_descr =  getattr( getattr(client.service[method.application.app_name], method.method_name), 'method')
    except:
        return inform_message(request, "Testing this method is not supported")

    in_name = method_descr.binding.input.bodypart_types(method_descr)[0]
    in_v =client.factory.create(in_name[0])
    variables = []
    for item in dir(in_v):
        if not item.startswith('__'):
            var = getattr(in_v,item)

            init_variable(var)

            variables.append(var)

    envelop = method_descr.binding.input.get_message(method_descr, variables,{})

    return render_to_response('method_test.html',{'envelop':envelop, 'menuitem':2, 'method':method})



#---------APP_DEPLOY------------------------



@authorize(APP_DEPLOY)
def undeploy_application(request, app_id):
    application = BasApplication.objects.get(id=app_id)

    client, inputVar = get_system_service('RequestUndeployApplication', application.cluster.id)
    inputVar.application_id = application.id

    try:
        ret = client.service.UndeployApplication(inputVar)
    except Exception, err:
        return inform_message(request, "Exception: %s"%err)

    if ret.ret_code != 0:
        return inform_message(request, "Error: %s"%ret.ret_message)

    request.session['last_url'] = '/applications'
    return inform_message(request, "Application is undeployed!")

@authorize(APP_DEPLOY)
def activate_application(request, app_id):
    application = BasApplication.objects.get(id=app_id)

    client, inputVar = get_system_service('RequestActivateApplication', application.cluster.id)
    inputVar.application_id = application.id

    try:
        ret = client.service.ActivateApplication(inputVar)
    except Exception, err:
        return inform_message(request, "Exception: %s"%err)

    if ret.ret_code != 0:
        return inform_message(request, "Error: %s"%ret.ret_message)

    request.session['last_url'] = '/application/%s' % app_id
    return inform_message(request, "Application with version %s is activated!"%application.app_version)

@authorize(APP_DEPLOY)
def deploy_application(request):
    cluster_id = int(request.session['cluster_id'])

    if request.method == 'POST':
        file_data =  request.FILES['appArchive']
        data = ''
        for chunk in file_data.chunks():
            data += chunk
        encSource = base64.encodestring(data)
        appName = request.POST['appName']
        appVersion = request.POST['appVersion']
        appType = request.POST['appType']

        client, inputVar = get_system_service('RequestDeployApplication', cluster_id)
        inputVar.app_name = appName
        inputVar.app_version = appVersion
        inputVar.app_type = appType
        inputVar.source = encSource

        try:
            ret = client.service.DeployApplication(inputVar)
        except Exception, err:
            return inform_message(request, "Exception: %s"%err)

        if ret.ret_code != 0:
            return inform_message(request, "Error: %s"%ret.ret_message)

        return inform_message(request, "Application is deployed!")


    return render_to_response('deploy_application.html',{'menuitem':2})

