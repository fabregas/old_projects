from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from models import *
from forms import *
from auth_app.views import *
from datetime import datetime, timedelta, date
from settings import NODE_SERVICE_WSDL,SYSTEM_SERVICE_WSDL, BAS_NODE_LOGIN,BAS_NODE_PASSWORD
from suds.client import Client
from django.db import transaction
from django.db.models import Min, Sum
import hashlib,json

#user roles
TOPOLOGY_READ = 'topology_read'
TOPOLOGY_MODIFY = 'topology_modify'
TOPOLOGY_ADMIN = 'topology_admin'

APP_READ = 'app_read'
APP_DEPLOY = 'app_deploy'
APP_ADMIN = 'app_admin'

USERS_READ = 'users_read'
USERS_ADMIN = 'users_admin'

#MENU constants
TOPOLOGY_MENU = 1
APPLICATIONS_MENU = 2
USERS_MENU = 3
ABOUT_MENU = 5


class Calendar:
    def __init__(self, dt, min_date):
        class Month:
            def __init__(self, num, descr):
                self.num = num
                self.descr = descr

        self.days = []
        self.months = []
        self.years = []
        MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5:'May', 6: 'June', 7: 'July',
            8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}

        for i in xrange(31):
            if dt.day == (i+1):
                self.days.insert(0,i+1)
            else:
                self.days.append(i+1)

        for i in xrange(12):
            month = Month(i+1, MONTHS[i+1])
            if dt.month == (i+1):
                self.months.insert(0,month)
            else:
                self.months.append(month)

        for year in range(min_date.year, date.today().year+1):
            if dt.year == year:
                self.years.insert(0, year)
            else:
                self.years.append(year)



def make_client_endpoint(client, hostname, path, cluster_id):
    conf = BasConfig.objects.get(config_type=1, config_object_id=cluster_id, param_name='system_transport')
    transport = conf.param_value.lower()
    if transport == 'https':
        conf = BasConfig.objects.get(config_type=1, config_object_id=cluster_id, param_name='ssl_port')
    else:
        conf = BasConfig.objects.get(config_type=1, config_object_id=cluster_id, param_name='http_port')

    client.options.location = '%s://%s:%s/%s' %(transport, hostname, conf.param_value,path)

    return client

class NodeInterfaces:
    ifaces = {}

    @classmethod
    def get(cls, node_id):
        node_id = int(node_id)
        return cls.ifaces[node_id]

    @classmethod
    def setup(cls):
        ifaces = {}
        nodes = BasClusterNode.objects.all()

        for node in nodes:
            client = Client(NODE_SERVICE_WSDL)

            ifaces[node.id] = make_client_endpoint(client, node.hostname, 'NodeManagement', node.cluster_id)

        cls.ifaces = ifaces


def inform_message(request, message):
    redirect_link = request.session.get('last_url','/')

    return render_to_response('inform_message.html',{'message':message, 'redirect_link':redirect_link})

def authorize(perm, save_path=False):
    def wraper(func):
        def dec_func(request, *args, **kvargs):
            if not is_authenticated(request):
                return HttpResponseRedirect('/login/')

            if not is_authorize(request, perm):
                return inform_message(request, 'You are not permissed for this action!')

            ret =  func(request, *args, **kvargs)

            if save_path:
                request.session['last_url'] = request.path

            return ret

        return dec_func
    return wraper


def index(request):
    clusters = BasCluster.objects.all()

    if len(clusters) == 1:
        return HttpResponseRedirect('/cluster_%i' % clusters[0].id)

    return HttpResponseRedirect('/clusters/')

def get_about(request):
    menuitem = ABOUT_MENU
    return render_to_response('about.html',{'menuitem':menuitem})


def exit(request):
    logout(request)
    return HttpResponseRedirect('/')


@authorize(USERS_READ, save_path=True)
def get_users(request):
    menuitem = users_menu

    users = basuser.objects.all().order_by('id')

    for user in users:
        roles = basuserroles.objects.filter(user=user.id)
        r_ids = [r.role.id for r in roles]
        roles = basrole.objects.filter(id__in = r_ids).order_by('id')

        user.roles = '\n'.join([r.role_name for r in roles])

    return render_to_response('users.html',{'menuitem':menuitem, 'users':users})


@authorize(USERS_READ, save_path=True)
def get_user(request, user_id):
    menuitem = USERS_MENU

    user = BasUser.objects.get(id=int(user_id))

    roles = BasUserRoles.objects.filter(user=user.id).order_by('role')
    user.roles = [r.role for r in roles]
    roles = BasRole.objects.all()

    if request.method == 'POST':
        if not is_authorize(request,USERS_ADMIN):
            return inform_message(request, 'You are not permissed for this action!')

        if user.name in ('bas_node_agent','root'): #system users... don't change it roles!
            return inform_message(request,"'%s' is system user!\n Don't change it roles" % user.name)

        f_roles = []
        for item in request.POST:
            if not item.startswith('role_'):
                continue

            f_roles.append( int(request.POST[item]) )

        #find new roles
        new_roles = []
        cur_roles = [r.id for r in user.roles]
        for role in f_roles:
            if role in cur_roles:
                continue
            new_roles.append(role)

        #find roles for delete
        del_roles = []
        for role in user.roles:
            if role.id in f_roles:
                continue
            del_roles.append(role.id)

        for role in new_roles:
            userRole = BasUserRoles(user=user, role_id=role)
            userRole.save()
        
        for role in del_roles:
            userRole = BasUserRoles.objects.get(user=user, role=role)
            userRole.delete()
        
        if new_roles or del_roles:
            return inform_message(request, "User roles is saved")

    return render_to_response('user_info.html',{'menuitem':menuitem, 'user':user, 'roles':roles})

@authorize(USERS_ADMIN)
def new_user(request):
    menuitem = USERS_MENU

    user = BasUser(name='',password_md5='')

    if request.method == 'POST':
        user.name = request.POST['userName']
        userPassword = request.POST['userPassword']

        md5 = hashlib.md5()
        md5.update(userPassword)
        user.password_md5 = md5.hexdigest()

        if BasUser.objects.filter(name=user.name):
            return inform_message(request, "User name '%s' is already exists in system"%user.name)

        user.save()

        return HttpResponseRedirect('/user_info/%i' % user.id)

    return render_to_response('new_user.html',{'menuitem':menuitem, 'user':user})


@authorize(USERS_READ)
def change_user_password(request, user_id):
    menuitem = USERS_MENU

    user = BasUser.objects.get(id=int(user_id))
    if not is_authorize(request, USERS_ADMIN):
        curr_user = get_current_user(request)
        
        if curr_user.id != user.id:
            return inform_message(request, 'You are not permissed for this action!')
    
    if user.name == 'bas_node_agent': #don't change it password from console!
        return inform_message(request,"Changing password for this user is not allowed" )

    if request.method == 'POST':
        newPassword = request.POST['newPassword']

        md5 = hashlib.md5()
        md5.update(newPassword)
        user.password_md5 = md5.hexdigest()

        user.save()

        return inform_message(request, "New password is saves for user '%s'"%user.name)

    return render_to_response('mod_user.html',{'menuitem':menuitem, 'user_id':user_id})


@authorize(USERS_ADMIN)
def delete_user(request, user_id):
    user = BasUser.objects.get(id=int(user_id))
    user_name = user.name

    if user_name in ('bas_node_agent','root'): #system users... don't delete it!
        return inform_message(request,"'%s' is system user!\n Deleting it is impossible!" % user_name)

    user.delete()

    request.session['last_url'] = '/users'
    return inform_message(request,"User '%s' is deleted!" % user_name)


NodeInterfaces.setup()

