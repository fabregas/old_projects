from IOTypesStructure import *
import os, tempfile, zipfile, sys, shutil
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


#--------------------------------------------------------------------------------------

sql_check_user_role = '''
        SELECT b_user.id
        FROM BAS_USER_ROLES user_role, BAS_USER b_user, BAS_ROLE b_role
        WHERE b_user.name = '%s'
            AND b_user.id = user_role.user_id
            AND user_role.role_id = b_role.id
            AND b_role.role_sid='%s'
'''

sql_get_user_passwd = "SELECT password_md5 FROM BAS_USER WHERE id=%i;"

#--------------------------------------------------------------------------------------


class NodeManagementApplicationImplementation:
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


    def StartApplication(self, request):
        err_code = 0
        err_message = 'Application started'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.start_application(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseStartApplication(ret_code=err_code, ret_message=err_message)

        return response

    def RenewApplicationCache(self, request):
        err_code = 0
        err_message = 'ok'
        app_id = request.application_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.renew_application_cache(app_id)
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

            (e_code, e_message) = self.server.stop_application(app_id)
            if e_code:
                raise Exception(e_code, e_message)

            (e_code, e_message) = self.server.start_application(app_id)
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

            (e_code, e_message) = self.server.stop_application(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseStopApplication(ret_code=err_code, ret_message=err_message)

        return response


    def LoadLibrary(self, request):
        err_code = 0
        err_message = 'Library loaded'
        app_id = request.library_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.load_shared_library(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseLoadLibrary(ret_code=err_code, ret_message=err_message)

        return response

    def UnloadLibrary(self, request):
        err_code = 0
        err_message = 'Library loaded'
        app_id = request.library_id

        try:
            self.authentication(request, 'app_admin')

            (e_code, e_message) = self.server.unload_shared_library(app_id)
            if e_code:
                raise Exception(e_code, e_message)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response = ResponseUnloadLibrary(ret_code=err_code, ret_message=err_message)

        return response


    def GetNodeStatistic(self, request):
        err_code = 0
        err_message = 'ok'
        response = ResponseGetNodeStatistic()

        try:
            self.authentication(request, 'topology_read')

            loadavgstr = open('/proc/loadavg', 'r').readline().strip()
            data = loadavgstr.split()

            rss = threads = ''
            lines = open('/proc/%i/status'%os.getpid(),'r').readlines()
            for line in lines:
                (param, value) = line.split()[:2]
                if param.startswith('VmRSS'):
                    rss = value.strip()
                elif param.startswith('Threads'):
                    threads = value.strip()

            res = resource.getrusage(resource.RUSAGE_SELF)

            response.statistic.loadavg_5 = data[0]
            response.statistic.loadavg_10 = data[1]
            response.statistic.loadavg_15 = data[2]
            response.statistic.utime = str(res.ru_utime)
            response.statistic.stime = str(res.ru_stime)
            response.statistic.memory = rss
            response.statistic.threads = threads
            response.statistic.uptime = str(datetime.now() - self.server.start_datetime)
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        response.ret_code = err_code
        response.ret_message = err_message
        return response

    def StartServerNode(self, request):
        raise Exception('METHOD IS NOT IMPLEMENTED')

    def RestartServerNode(self, request):
        import thread
        def restart():
            self.server.restart()

        thread.start_new_thread(restart, ())
        
        return ResponseRestartServerNode(ret_code=0, ret_message='Node is rebooting now! See log for details...')

    def StopServerNode(self, request):
        err_code = 0
        err_message = 'Server node is shuting down now...'

        try:
            self.authentication(request, 'topology_admin')

            thread.start_new_thread(self.server.stop, ())
        except Exception, e_obj:
            err_code, err_message = parse_exception(e_obj, self.debug)

        return ResponseStopServerNode(ret_code=err_code, ret_message=err_message)


#--------------------------------------------------------------------------------------
