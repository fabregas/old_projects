import os

AS_HOME = os.environ.get('BAS_HOME','')
AS_NODE_NAME = os.environ.get('BAS_NODE_NAME','')

AS_CONF_FILE = os.path.join(AS_HOME,'conf/bas_node.conf')
SSL_CERTIFICATE = os.path.join(AS_HOME,'conf/cert/server.crt')
SSL_PRIVATE_KEY = os.path.join(AS_HOME,'conf/cert/server.key')
AS_LOG_FILE  = os.path.join(AS_HOME, 'logs/application_server.log')
APPLICATION_DIR = os.path.join(AS_HOME, 'applications')
SHARED_LIB_DIR = os.path.join(AS_HOME, 'libraries')


if not AS_HOME:
    raise Exception("Environ variable BAS_HOME is not found in your OS")

if not AS_NODE_NAME:
    raise Exception ("Environ variable BAS_NODE_NAME is not found in your OS")
