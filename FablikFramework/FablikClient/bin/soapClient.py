
import urllib2, sys, logging, StringIO
import sudsWrap as sclient
from errorMessages import MESSAGES
from configManager import Config
from logManager import LogManager
import suds.client


class Client:
    logger = logging.getLogger('suds.client')
    log_handler = logging.StreamHandler(sys.stdout)
    interfaces = None

    @classmethod
    def set_logging(cls, log_file, log_level=logging.DEBUG):
        cls.logger.removeHandler(cls.log_handler)
        cls.log_handler.close()

        cls.log_handler = logging.StreamHandler(log_file)
        cls.logger = logging.getLogger('suds.client')
        cls.logger.setLevel(log_level)
        cls.logger.addHandler(cls.log_handler)

    @classmethod
    def authenticate(cls, username, password):
        iface = cls.get_interface('FABLIK_BASE')
        inputVar = iface.create_variable('RequestAuthenticate', login=username, password=password)

        result = iface.call('authenticate', inputVar)

        if result.ret_code != 0:
            message = MESSAGES.get(result.ret_code, result.ret_message)
            raise Exception(message)

        Config.setSessionID( result.session_id )
        Config.USER_NAME = username
        Config.USER_PASSWORD = password

        Config.ismod = True
        Config.save_config()

        cls.load_interfaces(iface)

    @classmethod
    def close_session(cls):
        if not Config.getSessionID():
            return

        iface = cls.get_interface('FABLIK_BASE')

        inputVar = iface.create_variable('RequestCloseSession', session_id=Config.getSessionID())

        result = iface.call('closeSession', inputVar)

        if result.ret_code != 0:
            message = MESSAGES.get(result.ret_code, result.ret_message)
            raise Exception(message)

    @classmethod
    def load_interfaces(cls, base_iface):
        inputVar = base_iface.create_variable('RequestGetInterfaces', session_id=Config.getSessionID())

        result = base_iface.call('getInterfaces', inputVar)

        if result.ret_code != 0:
            message = MESSAGES.get(result.ret_code, result.ret_message)
            raise Exception(message)

        if len(result.interface_list) == 0:
            return

        for interface in result.interface_list.interface:
            cls.interfaces[interface.sid] = interface.url


    @classmethod
    def get_interface(cls, iface_name):
        if cls.interfaces is None:
            cls.interfaces = {'FABLIK_BASE': Config.BASE_SERIVICE_URL}

        url = cls.interfaces.get(iface_name,None)

        if url is None:
            raise Exception('Interface "%s" is not found'%iface_name)

        is_ssl = False
        if url.startswith('https'):
            is_ssl = True

        iface = SoapInterface(url, is_ssl=is_ssl,
            username=Config.USER_NAME, password=Config.USER_PASSWORD)

        return iface





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

        self.client =  sclient.Client(wsdl_file)

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
        LogManager.debug('CALL %s method with input:\n%s' %(method_name, in_parameters))

        method = getattr(self.client.service, method_name)

        ret = method(in_parameters)

        LogManager.debug('CALL %s method results:\n%s' %(method_name, ret))

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


###Client.set_logging(sys.stdout,logging.INFO)
###Client.authenticate('fabregas','blik')
###Interfaces.load_interfaces()
#iface = Client.get_interface('FABLIK_BASE')

