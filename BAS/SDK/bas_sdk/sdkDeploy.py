
# Std.
import base64,os,sys
import urllib2
import httplib

# Suds.
from suds.client import Client
from suds.options import Options
from suds.transport import *
from suds.transport.http import HttpTransport

import logging

#logging.basicConfig(level=logging.DEBUG)


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



def deploy_to_bas(appName, appVersion, source, url, login, password, is_library):
    encSource = base64.encodestring(source)

    BAS_WSDL_FILE = os.path.join(url,'.wsdl')
    client =  Client(BAS_WSDL_FILE)

    if url.lower().startswith('https'):
        trans = HttpAuthUsingCert('/home/fabregas/work/BAS_new/server/conf/cert/server.crt','/home/fabregas/work/BAS_new/server/conf/cert/server.key')
        client.set_options(transport=trans)
    client.options.location = url

    inputVar = client.factory.create('RequestDeployApplication')
    inputVar.auth.login = login
    inputVar.auth.password = password
    inputVar.app_name = appName
    inputVar.app_version = appVersion
    if is_library:
        inputVar.app_type = 'shared_lib'
    else:
        inputVar.app_type = 'native_app'

    inputVar.source = encSource

    ret = client.service.DeployApplication(inputVar)
    #print ret

    return ret.ret_code, ret.ret_message


def test_connection(url, login, password):
    BAS_WSDL_FILE = 'file:./bas_system.wsdl'
    client =  Client(BAS_WSDL_FILE)

    if url.lower().startswith('https'):
        trans = HttpAuthUsingCert('/home/fabregas/work/BAS_new/server/conf/cert/server.crt','/home/fabregas/work/BAS_new/server/conf/cert/server.key')
        client.set_options(transport=trans)
    client.options.location = url

    inputVar = client.factory.create('RequestTest')
    inputVar.login = login
    inputVar.password = password

    print inputVar

    ret = client.service.Test(inputVar)

    return ret.ret_code, ret.ret_message



def parse_wsdl(url):
    BAS_WSDL_FILE = os.path.join(url,'.wsdl')

    client =  Client(BAS_WSDL_FILE)

    service = client.wsdl.services[0] #only one service supported

    NAME = service.name # append name to interface file
    for port in service.ports:
        methods = port.methods.keys()

        for method_name in methods:
            METHOD = port.methods[method_name] # append method to interface file

            INPUT = METHOD.soap.input.body.parts[0].root # input variable

            OUTPUT = METHOD.soap.output.body.parts[0].root # output variable



    print client.wsdl.types[0][0]
    print dir(client)

#parse_wsdl('http://192.168.80.92:33333/System/')
#print deploy_to_bas('appName','appVersion',"rrrr", 'http://192.168.80.83:33333/System/','test','testPsw')
