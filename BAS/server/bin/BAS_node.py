#!/usr/bin/python
# -*- coding: utf-8 -*-


import time, thread, socket, tempfile, os, sys, base64, shutil, zipfile,signal

try:
    from settings import *
except Exception, err:
    sys.stderr.write( 'ERROR: %s\n'%err )
    sys.exit(-1)

from WSGI import WSGIServer, WSGIDispatcher, SSLAdapter
from SystemApplication.Application import SystemApplication
from NodeManagementApplication.Application import NodeManagementApplication
from NodeManagementApplication import IOTypesStructure as STypes
from datetime import datetime,timedelta
from soaplib.client import make_service_client
from Exceptions import Error
from sql_queries import *
from ConfigASReader import Config
from AsyncWorkManager import AsyncThreadPool
import Logger, Database


class ApplicationServerBase:
    def __init__(self):
        self.server = None
        self.secure_server = None
        self.config = None
        self.database = None
        self.logger = None
        self.system_app = None
        self.cluster = []
        self.stoped = True
        self.stoping = True
        self.stoped = False
        self.dispatcher_stoped = True
        self.start_datetime = None


class LogApplicationServer (ApplicationServerBase):
    def __get_logs(self):
        log = self.server.wsgi_app.get_log_info()
        log_add = self.secure_server.wsgi_app.get_log_info()

        log.messages += log_add.messages
        log.statistic += log_add.statistic

        return log

    def log_dispatcher(self):
            ptime = timedelta()
            try:
                timeout = self.config.log_write_timeout
            except BaseException, err:
                    self.logger.log('[Statistic Dispatcher] log_write_timeout config parameter not found! Exiting from dispatcher', Logger.LL_ERROR)
                    return

            self.dispatcher_stoped = False

            while not self.stoping:
                try:
                    sleep_time = timeout - ptime.seconds

                    if sleep_time < 0:
                        sleep_time = 0
                    time.sleep(sleep_time)

                    d0 = datetime.now()

                    loginfo = self.__get_logs()


                    for stat in loginfo.statistic:
                        if (not stat.inputs) and (not stat.outputs) and (not stat.errors):
                            continue

                        self.database.modify(sql_insert_to_statlog % ( stat.app_id, self.config.node_id,datetime.now(), stat.inputs, stat.outputs, stat.errors))

                    for msg in loginfo.messages:
                        msg.message = msg.message.replace("'", '"')
                        self.database.modify(sql_insert_to_msglog % (msg.method_id, self.config.node_id, msg.sender,msg.method_type,msg.date, msg.message))

                    ptime = datetime.now() - d0
                except BaseException, err:
                    self.logger.log('[Statistic Dispatcher] ERROR: %s'%err, Logger.LL_ERROR)

            self.dispatcher_stoped = True


class ApplicationServer(LogApplicationServer):
    def __init_node(self):
        self.logger = Logger.Logger()

        self.config = Config(AS_CONF_FILE)

        try:
            self.database = Database.Database('host=%s user=%s dbname=%s'%(self.config.db_host, self.config.db_user, self.config.db_name))
        except Database.DBError, msg:
            raise Error(str(msg))

        self.logger.db_conn = self.database
        self.logger.node_id = self.config.node_id
        system_app = SystemApplication()
        node_mgt_app = NodeManagementApplication()

        self.logger.log('Application Server node starting...')

        system_app.start({'server':self})
        node_mgt_app.start({'server':self})

        system_app.id = -1
        node_mgt_app.id = -1
        self.system_app = system_app
        self.node_mgt_app = node_mgt_app

        http_apps = https_apps = {}
        if self.config.system_transport.lower() == 'https':
            https_apps = {'/System':system_app, '/NodeManagement':node_mgt_app }
            self.logger.log('System application starting over HTTPS transport...')
        else:
            http_apps = {'/System':system_app, '/NodeManagement':node_mgt_app }
            self.logger.log('System application starting over HTTP transport...')

        self.logger.log('Async task threads pool starting...')
        self.async_pool = AsyncThreadPool( dynamic_threading=True, min=1, max=20 ) #FIXME: make system parameters
        self.async_pool.start()


        self.logger.log('Node starting at host %s on ports %s (http) and %s (https)'%(self.config.as_host, self.config.http_port, self.config.ssl_port))
        self.server = WSGIServer( ( self.config.as_host, self.config.http_port ), WSGIDispatcher( http_apps ), maxthreads=self.config.max_threads )
        self.secure_server = WSGIServer( ( self.config.as_host, self.config.ssl_port ), WSGIDispatcher( https_apps ), maxthreads=self.config.max_threads )
        self.secure_server.ssl_adapter = SSLAdapter(SSL_CERTIFICATE,SSL_PRIVATE_KEY)

        sys.path.insert(1,'.')
        sys.path.insert(1,SHARED_LIB_DIR)
        sys.path.insert(1,APPLICATION_DIR)



    def start_application(self, app_id):
        raise Error('Method start_application is not implemented!')

    def stop_application(self, app_id):
        raise Error('Method stop_application is not implemented!')

    def start(self):
        try:
            self.__start()
        except Exception, err:
            if self.logger:
                self.logger.log("Exception: %s" % err)
            raise Exception(str(err))

    def __start(self):
        '''
        start application server in new thread
        '''
        self.__init_node()

        servers = self.database.execute(sql_get_all_cluster_nodes % self.config.cluster_id)

        for server in servers:
            if self.config.system_transport.lower() == 'https':
                client = make_service_client('https://%s:%s/NodeManagement'%(server[1],self.config.ssl_port), self.node_mgt_app)
                client.rem_port = self.config.ssl_port
            else:
                client = make_service_client('http://%s:%s/NodeManagement'%(server[1],self.config.http_port), self.node_mgt_app)
                client.rem_port = self.config.http_port

            client.rem_host = server[1]
            self.cluster.append( client )

        try:
            shutil.rmtree(APPLICATION_DIR)
            shutil.rmtree(SHARED_LIB_DIR)
        except: pass

        os.mkdir(APPLICATION_DIR)
        os.mkdir(SHARED_LIB_DIR)

        rets = self.database.execute(sql_get_shared_libraries % self.config.cluster_id)
        for id in rets:
            self.load_shared_library(id[0])

        rets = self.database.execute(sql_get_all_cluster_applications % self.config.cluster_id)
        for id in rets:
            self.start_application(id[0])


        self.stoped = False
        self.stoping = False
        thread.start_new_thread(self._start_thread,(self.server,))
        thread.start_new_thread(self._start_thread,(self.secure_server,))

        while (not self.server.ready) and (not self.stoped): #while staring
            time.sleep(1)

        while (not self.secure_server.ready) and (not self.stoped): #while staring
            time.sleep(1)

        if not self.stoped:
            self.logger.log('Application Server node started!')
            thread.start_new_thread(self.log_dispatcher, ())

        self.start_datetime = datetime.now()


    def _start_thread(self,server):
        try:
            server.start()
        except socket.error, msg:
            self.logger.log(str(msg), Logger.LL_ERROR)
        except BaseException, err:
            self.logger.log("[server error] - %s"%str(err), Logger.LL_ERROR)

        if not self.stoping:
            self.stop()

    def restart(self):
        '''
        restart applivation server node
        '''
        self.stop()
        self.start()

    def stop(self):
        '''
        stop application server node
        '''
        if not self.stoping:
            self.logger.log('Application Server node stoping...')
            self.stoping = True

            self.async_pool.stop()
            self.logger.log('Async threads pool stoped')

            rets = self.database.execute(sql_get_shared_libraries % self.config.cluster_id)
            for id in rets:
                self.unload_shared_library(id[0])

            rets = self.database.execute(sql_get_all_cluster_applications % self.config.cluster_id)
            for id in rets:
                self.stop_application(id[0])

            self.server.stop()
            self.secure_server.stop()

            while not self.dispatcher_stoped:
                time.sleep(1)

            self.logger.log('Application Server node stoped!')
            self.database.close()

            self.stoped = True


class ApplicationServerNode(ApplicationServer):
    def start_application(self, app_id):
        self.logger.log('Starting application [%i]'%app_id)

        (err_code, msg) = self.__start_application(app_id)

        log_level = Logger.LL_INFO
        if err_code:
            log_level = Logger.LL_ERROR

        self.logger.log(msg,log_level)

        return err_code, msg

    def __config_to_dict(self, in_list):
        ret_dict = {}

        for item in in_list:
            if item[2] == 2:
                ret_dict[item[0]] = int(item[1])
            elif item[2] in [1,4]:
                ret_dict[item[0]] = str(item[1])
            elif item[2] == 3:
                val = False
                if str(item[1]).lower() == 'true':
                    val = True
                ret_dict[item[0]] = val
            else:
                raise Exception('Config type is not found for parameter *%s*'%item[0])


        return ret_dict


    def __start_application(self, app_id):
        try:
            app = self.database.execute(sql_get_application % app_id)
            methods = self.database.execute(sql_get_app_methods % app_id)
            global_conf = self.database.execute(sql_get_global_config % (self.config.cluster_id ))
            app_conf = self.database.execute(sql_get_app_config % (app_id ))
        except Database.DBError, err:
            return (-1,str(err))

        if not app:
            return (-1, 'Application not in database')

        try:
            global_conf = self.__config_to_dict(global_conf)
            app_conf = self.__config_to_dict(app_conf)
            global_conf.update(app_conf)
        except Exception, err:
            return (-10,'Configuretion reading error. Details: %s'%err)

        try:
            app = app[0]

            active_flag = app[4]
            if int(active_flag) == 0:
                return (-2, "Application {%i} is not active. Don't started!" % app_id)

            is_secure = app[3] & 16
            if is_secure:
                if self.secure_server.wsgi_app.is_application_started(app_id):
                    return (0, 'Application {%i} is already started'%app_id)
            else:
                if self.server.wsgi_app.is_application_started(app_id):
                    return (0, 'Application {%i} is already started'%app_id)


            #LOAD APPLICATION
            tmp = open(os.path.join(tempfile.gettempdir(), 'basApp.tmp'),'wb')

            tmp.write(base64.decodestring(str(app[5])))
            tmp.close()

            source_file = zipfile.ZipFile(tmp.name)

            app_home_path = os.path.join(APPLICATION_DIR,'%s'%(app[1]))

            try:
                shutil.rmtree(app_home_path)
            except: pass
            os.mkdir(app_home_path)

            source_file.extractall(app_home_path)
            os.unlink(tmp.name)


            exec("from %s.Application import %s"%(app[1], app[1]))
            exec("application = %s()"%app[1])


            application.id = app_id
            application.name = app[1]
            application.version = app[2]
            application.path = "/%s"%app[1]

            for method in methods:
                if (method[1] & 2):
                    application.incomming[method[0]] = method[2]
                if (method[1] & 4):
                    application.outgoing[method[0]] = method[2]
                application.methods_list[method[0]] = method[2]

            application.log_statistic = 1 #app[3] & 1

            try:
                application.start(global_conf)
            except Exception, err:
                self.stop_application(app_id)
                raise Exception(err)

            #print is_secure,  application.log_outgoing, application.log_incomming,  application.log_statistic 

            if is_secure:
                self.secure_server.wsgi_app.append(application)
            else:
                self.server.wsgi_app.append(application)
        except Exception, err:
            return (-1,'Application <%s %s> starting failed. [%s]'%(app[1],app[2],err))

        return (0, 'Application <[%i] %s %s> started successful'%(app[0],app[1],app[2]))


    def stop_application(self, app_id):
        self.logger.log('Application [%i] is stoping now'%app_id)
        app_name = ''

        try:
            app = self.server.wsgi_app.stop(app_id)
            if not app:
                app = self.secure_server.wsgi_app.stop(app_id)

            if not app:
                self.logger.log('Application [%i] is not started'%(app_id))

                app = self.database.execute(sql_get_application % app_id)
                app_name = app[0][1]

                return (0, 'Application with ID %i is not started' % app_id)


            app_name = app[1].name
            try:
                app[1].stop()
            except Exception, err:
                raise Exception(err)
            finally:
                shutil.rmtree(os.path.join(APPLICATION_DIR, app[1].name))
        except Exception, msg:
            self.logger.log('Application <[%i] %s %s> stoping error <%s>'%(app_id, app[1].name, app[1].version, msg), Logger.LL_ERROR)
            return (-2, msg)
        finally:
            #remove related modules...
            rem = [app_name]
            for item in sys.modules:
                if item.startswith(app_name+'.'):
                    rem.append(item)

            for item in rem:
                mod = sys.modules.pop(item,'')
                del mod

        self.logger.log('Application [%i] stoped'%(app_id))

        return (0,'ok')

    def renew_application_cache(self, app_id):
        self.logger.log('Application [%i] is renewing cache'%app_id)

        try:
            global_conf = self.database.execute(sql_get_global_config % (self.config.cluster_id ))
            app_conf = self.database.execute(sql_get_app_config % (app_id ))

            global_conf = self.__config_to_dict(global_conf)
            app_conf = self.__config_to_dict(app_conf)

            global_conf.update(app_conf)

            ret = self.server.wsgi_app.syncronize_application(app_id, global_conf)
            if not ret:
                ret = self.secure_server.wsgi_app.syncronize_application(app_id, global_conf)

            if not ret:
                return (0, 'Application with ID %i is not found' % app_id)

        except Exception, msg:
            self.logger.log('Application [%i] renew cache error <%s>'%(app_id, msg), Logger.LL_ERROR)
            return (-2, msg)

        self.logger.log('Application [%i] renew cache'%(app_id))

        return (0,'ok')

    def is_application_started(self, app_id):
        return self.server.wsgi_app.is_application_started(app_id)


    def load_shared_library(self, app_id):
        try:
            app = self.database.execute(sql_get_application % app_id)
        except Database.DBError, err:
            return (-1,str(err))

        if not app:
            return (-1, 'Library {%i} is not in database'%app_id)

        app = app[0]

        active_flag = app[4]
        if int(active_flag) == 0:
            return (-2, "Library {%i} is not active. Don't started!" % app_id)


        #LOAD LIBRARY
        try:
            tmp = open(os.path.join(tempfile.gettempdir(), 'basLib.tmp'),'wb')

            tmp.write(base64.decodestring(str(app[5])))
            tmp.close()

            source_file = zipfile.ZipFile(tmp.name)

            app_home_path = os.path.join(SHARED_LIB_DIR,'%s'%(app[1]))
            try:
                shutil.rmtree(app_home_path)
            except: pass
            os.mkdir(app_home_path)

            source_file.extractall(app_home_path)
            os.unlink(tmp.name)
        except Exception, err:
            return (-1,'Library <%s %s> loading failed. [%s]'%(app[1],app[2],err))

        ret_message = 'Library <[%i] %s %s> loaded successful'%(app[0],app[1],app[2])
        self.logger.log(ret_message)

        return (0, ret_message)



    def unload_shared_library(self, app_id):
        app_name = None
        try:
            app = self.database.execute(sql_get_application % app_id)

            if not app:
                return (-1, 'Library {%i} is not in database'%app_id)

            app = app[0]

            app_name = app[1]
            app_home_path = os.path.join(SHARED_LIB_DIR,'%s'%(app_name))
            shutil.rmtree(app_home_path)
        finally:
            #remove related modules...
            if app_name is not None:
                rem = [app_name]
                for item in sys.modules:
                    if item.startswith(app_name+'.'):
                        rem.append(item)

                for item in rem:
                    mod = sys.modules.pop(item,'')
                    del mod

        msg = 'Library <[%i] %s %s> unloaded successful'%(app[0],app[1],app[2])
        self.logger.log(msg)
        return (0, msg)


    def load_library_in_cluster(self, id):
        request = STypes.RequestLoadLibrary()
        request.auth.login = self.config.bas_username
        request.auth.password = self.config.bas_password
        request.library_id = id

        err = ''
        for server in self.cluster:
            ret = None
            msg = ''
            try:
                ret = server.LoadLibrary(request)
            except Exception, e:
                msg = 'Load library on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,e)
            finally:
                if ret and ret.ret_code != 0:
                    msg = 'Load library on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,ret.ret_message)

                if msg:
                    self.logger.log(msg, Logger.LL_WARNING)
                    err += '%s\n' % msg

        if err:
            return (-1, 'Library is not loaded on some nodes in cluster. Details:\n%s'%err)

        return (0,'Library loaded in cluster')


    def unload_library_in_cluster(self, id):
        request = STypes.RequestUnloadLibrary()
        request.auth.login = self.config.bas_username
        request.auth.password = self.config.bas_password
        request.library_id = id

        err = ''
        for server in self.cluster:
            ret = None
            msg = ''

            try:
                ret = server.UnloadLibrary(request)
            except Exception, err:
                self.logger.log('Unload library on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,err),Logger.LL_WARNING)
            finally:
                if ret and ret.ret_code != 0:
                    msg = 'Unload library on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,ret.ret_message)

                if msg:
                    self.logger.log(msg, Logger.LL_WARNING)
                    err = '%s\n' % msg

        if err:
            return (-1, 'Library is not unloaded on some nodes in cluster. Details:\n%s' % err)

        return (0,'Application is unloaded in cluster')


    def start_application_in_cluster(self, id):
        request = STypes.RequestStartApplication()
        request.auth.login = self.config.bas_username
        request.auth.password = self.config.bas_password
        request.application_id = id

        err = ''
        for server in self.cluster:
            ret = None
            msg = ''
            try:
                ret = server.StartApplication(request)
            except Exception, e:
                msg = 'Start application on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,e)
            finally:
                if ret and ret.ret_code != 0:
                    msg = 'Start application on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,ret.ret_message)

                if msg:
                    self.logger.log(msg, Logger.LL_WARNING)
                    err += '%s\n' % msg

        if err:
            return (-1, 'Application is not started on some nodes in cluster. Details:\n%s'%err)


        return (0,'Application is started in cluster')


    def renew_application_cache_in_cluster(self, id):
        request = STypes.RequestRenewApplicationCache()
        request.auth.login = self.config.bas_username
        request.auth.password = self.config.bas_password
        request.application_id = id

        err = ''
        for server in self.cluster:
            ret = None
            msg = ''

            try:
                ret = server.RenewApplicationCache(request)
            except Exception, e:
                msg = 'Renew application cache on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,e)
            finally:
                if ret and ret.ret_code != 0:
                    msg = 'Renew application cache on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,ret.ret_message)

                if msg:
                    self.logger.log(msg, Logger.LL_WARNING)
                    err = '%s\n' % msg

        if err:
            return (-1, 'Application is not renew cache on same nodes in cluster. Details:\n%s' % err)

        return (0,'Application is renew cache in cluster')


    def stop_application_in_cluster(self, id):
        request = STypes.RequestStopApplication()
        request.auth.login = self.config.bas_username
        request.auth.password = self.config.bas_password
        request.application_id = id

        err = ''
        for server in self.cluster:
            ret = None
            msg = ''

            try:
                ret = server.StopApplication(request)
            except Exception, err:
                msg = 'Stop application on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,err)
            finally:
                if ret and ret.ret_code != 0:
                    msg = 'Stop application on [%s:%i] is failed. {%s}'%(server.rem_host,server.rem_port,ret.ret_message)

                if msg:
                    self.logger.log(msg, Logger.LL_WARNING)
                    err = '%s\n' % msg

        if err:
            return (-1, 'Application is not stoped on same nodes in cluster. Details:\n%s' % err)

        return (0,'Application is stoped in cluster')


#---------------------------------------------------------------------------------------------------------


class NodeManager:
    node = None

    @classmethod
    def start(cls):
        try:
            cls.node = ApplicationServerNode()

            cls.node.start()
        except Exception, err:
            try:
                cls.node.stop()
            except: pass
            sys.stderr.write("%s\n" %err)
            sys.exit(-2)


    @classmethod
    def stop(cls):
        try:
            cls.node.stop()
            sys.exit(0)
        except Exception, err:
            sys.stderr.write('%s\n' %err)
            sys.exit(-3)

    @classmethod
    def restart(cls):
        try:
            cls.node.restart()
        except Exception, err:
            sys.stderr.write('%s\n' %err)
            sys.exit(-4)


#---------------------------------------------------------------------------------------------------------

def restart_handler(sig, arg):
    NodeManager.restart()

def stop_handler(sig, arg):
    NodeManager.stop()

signal.signal(signal.SIGHUP, restart_handler)
signal.signal(signal.SIGINT, stop_handler)


NodeManager.start()

while True:
    time.sleep(1)

#---------------------------------------------------------------------------------------------------------

