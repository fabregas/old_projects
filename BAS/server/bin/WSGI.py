
from wsgiserver import CherryPyWSGIServer
from wsgiserver.ssl_pyopenssl import pyOpenSSLAdapter
import soaplib.wsgi_soap
import thread
from datetime import datetime

from soaplib.service import soapmethod

class SSLAdapter(pyOpenSSLAdapter):
    pass


class LogInfo:
    def __init__(self):
        self.messages = []
        self.statistic = []


class WSGIPathInfoDispatcher(object):
    """A WSGI dispatcher for dispatch based on the PATH_INFO.
    
    apps: a dict or list of (path_prefix, app) pairs.
    """
    
    def __init__(self, apps):
        self.__lock = thread.allocate_lock()
        try:
            apps = apps.items()
        except AttributeError:
            pass
        
        # Sort the apps by len(path), descending
        apps.sort(cmp=lambda x,y: cmp(len(x[0]), len(y[0])))
        apps.reverse()
        
        # The path_prefix strings must start, but not end, with a slash.
        # Use "" instead of "/".
        self.apps = [(p.rstrip("/"), a) for p, a in apps]
    
    def __get_applications(self):
        self.__lock.acquire_lock()
        try:
            ret = self.apps
        finally:
            self.__lock.release_lock()

        return ret

    def __call__(self, environ, start_response):
        path = environ["PATH_INFO"] or "/"
        for p, app in self.__get_applications():
            # The apps list should be sorted by length, descending.
            if path.startswith(p + "/") or path == p:
                environ = environ.copy()
                environ["SCRIPT_NAME"] = environ["SCRIPT_NAME"] + p
                environ["PATH_INFO"] = path[len(p):]
                return app(environ, start_response)
        
        start_response('404 Not Found', [('Content-Type', 'text/plain'),
                                         ('Content-Length', '0')])
        return ['']

    def get_log_info(self):
        log = LogInfo()

        for (path, app) in self.apps:
            log.messages += app.get_messages()
            log.statistic.append(app.get_statistic())

        return log


    def is_application_started(self, app_id):
        ret = False
        applications = self.__get_applications()

        for path, app in applications:
            if app.id == app_id:
                ret =  True

        return ret

    def append(self, application):
        self.__lock.acquire_lock()
        try:
            self.apps.append((application.path, application))

            self.apps.sort(cmp=lambda x,y: cmp(len(x[0]), len(y[0])))
            self.apps.reverse()
        finally:
            self.__lock.release_lock()


    def stop(self, app_id):
        f_app = -1
        i = 0

        self.__lock.acquire_lock()

        try:
            for p, app in self.apps:
                if app.id == app_id:
                    f_app = i
                    break
                i += 1

            if f_app < 0:
                return None

            ret_app = self.apps[f_app]

            del self.apps[f_app]
            #self.apps.sort(cmp=lambda x,y: cmp(len(x[0]), len(y[0])))
            self.apps.reverse()
        finally:
            self.__lock.release_lock()

        return ret_app

    def syncronize_application(self, app_id, config):
        founded = False

        for path, app in self.__get_applications():
            if app.id == app_id:
                founded = True
                app.syncronize(config)
                break

        return founded


class WSGIDispatcher(WSGIPathInfoDispatcher):
    pass


class WSGIServer(CherryPyWSGIServer):
    pass

#MESSAGE TYPES
MT_INPUT = 1
MT_OUTPUT = 2
MT_ERROR = 3

class Message:
    def __init__(self, method_id, dtime, message, sender, m_type):
        self.method_id = method_id
        self.date = dtime
        self.message = message
        self.method_type = m_type
        self.sender = sender

class Statistic:
    def __init__(self):
        self.app_id = -1
        self.inputs = 0
        self.outputs = 0
        self.errors = 0


class Application(soaplib.wsgi_soap.SimpleWSGISoapApp):
    def __init__(self):
        soaplib.wsgi_soap.SimpleWSGISoapApp.__init__(self)
        self.__in_messages = []
        self.__out_messages = []
        self.__err_messages = []
        self.incomming = {}
        self.outgoing = {}
        self.methods_list = {}
        self.log_statistic = False
        self.statistic = Statistic()
        self.__lock = thread.allocate_lock()
        self.config = {}


    def start(self, config={}):
        self.config = config

    def stop(self):
        pass

    def _auth_user(self, login, password):
        #Implement this method if you need authenticate your ssl session
        return 0

    def synchronize(self, config={}):
        #Implement this method for renew your cached objects
        pass

    def get_messages(self):
        self.__lock.acquire_lock()
        try:
            ret = self.__in_messages + self.__out_messages + self.__err_messages
            self.__in_messages = []
            self.__out_messages = []
            self.__err_messages = []
        finally:
            self.__lock.release_lock()

        return ret

    def get_statistic(self):
        self.__lock.acquire_lock()
        try:
            ret = self.statistic
            ret.app_id = self.id
            self.statistic = Statistic()
        finally:
            self.__lock.release_lock()

        return ret

    def onWsdl(self,environ,wsdl):
        #print environ
        pass

    def onCall(self,environ):
        pass

    def onMethodExec(self,environ,body,py_params, method):
        self.__lock.acquire_lock()
        try:
            method_id = self.incomming.get(method, None)
            if method_id:
                sender = environ.get('REMOTE_ADDR','null')

                self.__in_messages.append( Message(method_id, datetime.now(), body, sender, MT_INPUT) )

            if self.log_statistic:
                self.statistic.inputs += 1
        finally:
            self.__lock.release_lock()


    def onReturn(self, environ, ret_string):
        self.__lock.acquire_lock()
        try:
            method_name = environ['HTTP_SOAPACTION']
            if method_name.startswith('"'):
                method_name = method_name[1:-1]

            method_id = self.outgoing.get(method_name,None)

            if method_id:
                sender = environ.get('REMOTE_ADDR','null')

                self.__out_messages.append( Message(method_id, datetime.now(), ret_string, sender, MT_OUTPUT) )

            if self.log_statistic:
                self.statistic.outputs += 1
        finally:
            self.__lock.release_lock()


    def onException(self,environ,exc,resp):
        self.__lock.acquire_lock()
        try:
            debug = self.config.get('DEBUG', True)

            if debug:
                method_name = environ['HTTP_SOAPACTION']
                if method_name.startswith('"'):
                    method_name = method_name[1:-1]
                method_id = self.methods_list.get(method_name,None)
                self.__err_messages.append( Message(method_id, datetime.now(), resp,'', MT_ERROR) )
            if self.log_statistic:
                self.statistic.errors += 1
        finally:
            self.__lock.release_lock()
