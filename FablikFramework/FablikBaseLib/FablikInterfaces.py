# Std.
import urllib2
import httplib

# Suds.
from suds.client import Client
from suds.options import Options
from suds.transport import *
from suds.transport.http import HttpTransport

import sql_fablik_lib as SQL
from Database import Database
from SharedDBConnection import DBConnection
from FablikErrorCodes import *


class HTTPSClientAuthHandler(urllib2.HTTPSHandler):
    """HTTPS Client Auth solution for urllib2.

    Inspired by http://bugs.python.org/issue3466 and improved by David Norton
    of Three Pillar Software. In this implementation, we use properties passed
    in rather than static module fields.

    Found at: http://www.threepillarsoftware.com/soap_client_auth
    """
    def __init__(self, cert, key):
        urllib2.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        """
        Rather than pass in a reference to a connection class, we pass in
        a reference to a function which, for all intents and purposes,
        will behave as a constructor
        """
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httplib.HTTPSConnection(host, key_file=self.key, cert_file=self.cert)

class HttpAuthUsingCert(HttpTransport):
    """Provides http authentication using certificate and key.

    @ivar handler: The authentication handler.
    @ivar cert: Path to PEM certificate file.
    @ivar key: Path to PEM private key file.
    """
    #def __init__(self, cert, key, options=Options()):
    def __init__(self, cert, key):
        HttpTransport.__init__(self)
        self.handler = HTTPSClientAuthHandler(cert, key)
        self.urlopener = urllib2.build_opener(self.handler)

    def open(self, request):
        return  HttpTransport.open(self, request)

    def send(self, request):
        return HttpTransport.send(self, request)


class SoapInterface:
    """
    This class repsent wraper for SOAP client
    """

    def __init__(self, wsdl_file, endpoint=None, is_ssl=False, username=None, password=None):
        '''
        Constructor method

        @wsdl_file - URL representing WSDL file (local or global URL)
        @endpoint   - SOAP endpoint URL
        @is_ssl     - if True  then initiate ssl connection
        @username   - username for HTTP authentication (if None then no HTTP authentication)
        @password   - password for HTTP authentication
        '''

        self.client =  Client(wsdl_file)

        if is_ssl:
            trans = HttpAuthUsingCert('','')
            self.client.set_options(transport=trans)

        if endpoint is not None:
            self.client.options.location = endpoint

        if is_ssl and username:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, endpoint, username, password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            self.client.options.transport.urlopener  = urllib2.build_opener(authhandler)


    def call(self, method_name, *in_parameters):
        '''
        Call SOAP method with some input parameters

        @method_name    - SOAP method name for calling
        @in_parameters  - comma-separated list of input parameters

        @return         - SOAP response object
        '''

        method = getattr(self.client.service, method_name)

        ret = method(in_parameters)

        return ret


    def create_variable(self, var_name, **values):
        '''
        Create variable object by name (from WSDL definition)

        @var_name   - variable name (with namespase if it occur)
        @values     - values map (param_name, param_value)
        @return     - variable object
        '''

        var = self.client.factory.create(var_name)

        for item in values:
            setattr(var, item, values[item])

        return var


class InterfaceManager:
    def __init__(self, config):
        DATABASE_STRING = config.get('FB_DATABASE_STRING',None)
        DATABASE_PSWD = config.get('FB_DATABASE_PASSWORD',None)

        if DATABASE_STRING is None or DATABASE_PSWD is None:
            raise Exception(FBE_CONFIG_ERROR, 'FB_DATABASE_STRING and FB_DATABASE_PASSWORD must be set for this cluster')

        self.database = DBConnection.create_connection( DATABASE_STRING % DATABASE_PSWD )

    def getServiceInterface(self, interface_sid):
        iface = self.database.execute(SQL.get_interface_by_sid % interface_sid)

        if not iface:
            raise Exception (FBE_INVALID_INTERFACE, 'Interface %s is not found' % interface_sid)

        (url, db_conn_string) = iface[0]

        if not url:
            raise Exception (FBE_INVALID_SERVICE_URL, 'Service URL is empty for interface %s' % interface_sid)

        #make service
        service = SoapInterface(url) #FIXME: implement SSL+Auth support

        return service

    def getDatabaseInterface(self, interface_sid):
        iface = self.database.execute(SQL.get_interface_by_sid % interface_sid)

        if not iface:
            raise Exception (FBE_INVALID_INTERFACE, 'Interface %s is not found' % interface_sid)

        (url, db_conn_string) = iface[0]

        if not db_conn_string:
            raise Exception (FBE_INVALID_DB_STRING, 'Database connection string is empty for interface %s' % interface_sid)

        try:
            db_conn = Database(db_conn_string)
        except Exception ,err:
            raise Exception (FBE_INVALID_DB_CONNECT, 'Database connection is not esteblish! Details: %s' % err)

        return db_conn

    def getDatabaseInterfaceByID(self, interface_id):
        iface = self.database.execute(SQL.get_interface_by_id % interface_id)

        if not iface:
            raise Exception (FBE_INVALID_INTERFACE, 'Interface with ID %s is not found' % interface_id)

        (url, db_conn_string) = iface[0]

        if not db_conn_string:
            raise Exception (FBE_INVALID_DB_STRING, 'Database connection string is empty for interface with ID %s' % interface_id)

        try:
            db_conn = Database(db_conn_string)
        except Exception, err:
            raise Exception (FBE_INVALID_DB_CONNECT, 'Database connection is not esteblish! Details: %s' % err)

        return db_conn
