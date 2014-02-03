from IOTypesStructure import *
import os, tempfile, zipfile, sys, shutil
from sys_sql_queries import *
import traceback, hashlib, base64, resource, thread
from datetime import datetime

ERR_UNEXPECTED = -666

def parse_exception(e_obj, debug):
    if len(e_obj.args) == 2:
        (err_code, err_message) = e_obj.args
    else:
        (err_code,err_message) = (ERR_UNEXPECTED, str(e_obj))

    if debug:
        err_message += '\n' + '-'*80 + '\n'
        err_message += ''.join(apply(traceback.format_exception, sys.exc_info()))
        err_message += '-'*80 + '\n'

    return (err_code, err_message)


def get_app_methods(app_name, app_data):
    ret_methods = None

    tmp = open(os.path.join(tempfile.gettempdir(), 'basApp.tmp'),'wb')
    tmp.write(app_data)
    tmp.close()

    source_file = zipfile.ZipFile(tmp.name)

    tmp_path = tempfile.mkdtemp()
    tmp_dir = os.path.dirname(tmp_path)
    tmp_base = os.path.basename(tmp_path)

    source_file.extractall(tmp_path)
    os.unlink(tmp.name)

    curdir = os.path.abspath(os.curdir)

    if sys.path.count('') == 0:
        sys.path.append('')

    os.chdir(tmp_dir)

    try:
        exec("from %s.Application import %s"%(tmp_base,app_name))
        exec("application = %s()"%app_name)

        methods = application.methods()
        ret_methods = [method.name for method in methods]
    finally:
        os.chdir(curdir)
        rem = [tmp_base]
        for item in sys.modules:
            if item.startswith(tmp_base+'.'):
                rem.append(item)

        for item in rem:
            mod = sys.modules.pop(item,'')
            del mod
        shutil.rmtree(tmp_path)


    return ret_methods



#--------------------------------------------------------------------------------------



class SystemApplicationImplementation:
    def authentication(self, request, role):
        login = request.auth.login
        password = request.auth.password

        user = self.db_conn.execute( sql_check_user_role % (login, role))
        if not user:
            raise Exception (-1, 'User is not found or dont has %s role' % role)

        passwd = self.db_conn.execute( sql_get_user_passwd % user[0][0])

        if not passwd:
            raise Exception (-1,'User password is invalid!')

        passwd = passwd[0][0]

        md5 = hashlib.md5()
        md5.update(password)
        passwd_md5 = md5.hexdigest()

        if passwd != passwd_md5:
            raise Exception (-1,'Password is invalid!')


    def start_routine(self, config):
        self.server = config.get('server', None)
        self.debug = config.get('DEBUG',0)

        if self.server is None:
            raise Exception ('System application need node manager instance (expected "server" parameter)')

        self.db_conn = self.server.database


    def syncronize_application(self, config):
        pass

    def stop_routine(self):
        pass


    def DeployApplication(self, request):
        err_code = 0
        err_message = 'Application deployed'

        db_conn = self.db_conn
        cluster_id = self.server.config.cluster_id
        app_name = request.app_name
        app_version = request.app_version
        source = request.source.data
        app_type = request.app_type
        active_app_id = None
        new_id = None

        try:
            self.authentication(request, 'app_deploy')

            if app_type not in ['native_app','shared_lib']:
                raise Exception (-4, 'Application type %s is not supported. Supported types are native_app and shared_lib' % app_type)

            #check application type
            ret = db_conn.execute(sql_get_app_type_by_name % (cluster_id, app_name))
            if ret and ret[0][0] != app_type:
                raise Exception (-5, 'Application <%s> is already exists on server and it is type is %s.'%(app_name,ret[0][0]))

            #check application version
            ret = db_conn.execute(sql_get_app_by_version % (cluster_id, app_name, app_version))
            if ret:
                raise Exception (-3, 'Application <%s> with version <%s> is already exists on server.'%(app_name,app_version))

            if app_type == 'native_app':
                methods = get_app_methods(app_name, source)
                if methods is None:
                    raise Exception (-2, 'Getting methods from application failed!')
            else:
                methods = []

            ret = db_conn.execute(sql_get_active_app % (cluster_id, app_name))
            if ret:
                active_app_id = ret[0][0]

            #begin DB transaction
            db_conn.start_transaction()

            db_conn.modify(sql_update_application % (cluster_id, app_name))

            db_conn.modify(sql_insert_application %(cluster_id, app_name, app_version, app_type, 0, datetime.now(), base64.encodestring(source)))

            new_id = db_conn.execute(sql_get_active_app % (cluster_id, app_name))[0][0] #FIXME

            if app_type == 'native_app' and active_app_id:
                db_conn.modify(sql_update_config %(new_id, active_app_id))

            for method in methods:
                db_conn.modify( sql_insert_app_method % (new_id, method))

            # end DB transaction  
            db_conn.end_transaction()

            if app_type == 'native_app':
                #stop old version in cluster (if exists)
                if active_app_id is not None:
                    self.server.stop_application_in_cluster(active_app_id)
                #start application in cluster
                self.server.start_application_in_cluster(new_id)
            elif app_type == 'shared_lib':
                #unload old shared library in cluster (if exists)
                if active_app_id is not None:
                    self.server.unload_library_in_cluster(active_app_id)
                #load shared library in cluster
                self.server.load_library_in_cluster(new_id)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj,self.debug)

        response = ResponseDeployApplication(ret_code=err_code, ret_message=err_message, application_id=new_id)

        return response

    def ActivateApplication(self, request):
        err_code = 0
        err_message = 'Application activated'

        db_conn = self.db_conn
        cluster_id = self.server.config.cluster_id
        app_id = request.application_id

        try:
            self.authentication(request, 'app_deploy')

            db_conn.start_transaction()

            try:
                app = db_conn.execute(sql_get_application_by_id % (app_id))

                if not app:
                    raise Exception(-18, 'Application with ID %i is not found!')
                else:
                    app_name,app_type = app[0]

                active_app_id = db_conn.execute(sql_get_active_app % (cluster_id, app_name))[0][0]

                db_conn.modify(sql_update_application % (cluster_id, app_name))
                db_conn.modify(sql_activate_application % (app_id))
            finally:
                # end DB transaction  
                db_conn.end_transaction()

            if app_type == 'native_app':
                #stop old version in cluster
                self.server.stop_application_in_cluster(active_app_id)
                #start application in cluster
                self.server.start_application_in_cluster(app_id)
            elif app_type == 'shared_lib':
                #unload old shared library in cluster
                self.server.unload_library_in_cluster(active_app_id)
                #load shared library in cluster
                self.server.load_library_in_cluster(app_id)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj,self.debug)

        response = ResponseActivateApplication(ret_code=err_code, ret_message=err_message)

        return response

    def UndeployApplication(self, request):
        err_code = 0
        err_message = 'Application undeployed'

        db_conn = self.db_conn
        cluster_id = self.server.config.cluster_id
        app_id = request.application_id

        try:
            self.authentication(request, 'app_deploy')

            app_type = db_conn.execute(sql_get_application_type % app_id)
            if not app_type:
                raise Exception(-12, 'Application {%i} is not found in database'%app_id)
            app_type = app_type[0][0]

            if app_type == 'native_app':
                #stop application in cluster
                (e_code, err_message) = self.server.stop_application(app_id)
            elif app_type == 'shared_lib':
                #load shared library in cluster
                (e_code, err_message) = self.server.unload_library_in_cluster(app_id)

            #begin DB transaction
            db_conn.start_transaction()

            db_conn.modify(sql_remove_app_logs % (app_id))
            db_conn.modify(sql_remove_app_stats %(app_id))

            next_app_id = db_conn.execute(sql_get_next_active_app %(app_id, app_id))

            if next_app_id[0][0]:
                db_conn.modify(sql_update_config %(next_app_id[0][0], app_id))
                db_conn.modify(sql_activate_application %(next_app_id[0][0]))
            else:
                db_conn.modify(sql_remove_app_config %(app_id))

            db_conn.modify(sql_remove_app_methods %(app_id))
            db_conn.modify(sql_remove_application %(app_id))

            # end DB transaction  
            db_conn.end_transaction()

        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj,self.debug)

        response = ResponseUndeployApplication(ret_code=err_code, ret_message=err_message)

        return response


    def StartApplication(self, request):
        err_code = 0
        err_message = 'Application started'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.start_application_in_cluster(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj,self.debug)

        response = ResponseStartApplication(ret_code=err_code, ret_message=err_message)

        return response

    def RenewApplicationCache(self, request):
        err_code = 0
        err_message = 'ok'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.renew_application_cache_in_cluster(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)


        return ResponseRenewApplicationCache(ret_code=err_code, ret_message=err_message)


    def RestartApplication(self, request):
        err_code = 0
        err_message = 'Application restarted'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.stop_application_in_cluster(app_id)

            (e_code, e_message) = self.server.start_application_in_cluster(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseRestartApplication(ret_code=err_code, ret_message=err_message)

        return response


    def StopApplication(self, request):
        err_code = 0
        err_message = 'Application stoped'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.stop_application_in_cluster(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseStopApplication(ret_code=err_code, ret_message=err_message)

        return response


    def GetApplicationState(self, request):
        err_code, err_message, state = 0, '', ''
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            if self.server.is_application_started(app_id):
                state = 'up'
            else:
                state = 'down'
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseGetApplicationState(ret_code=err_code, ret_message=err_message, state=state)
