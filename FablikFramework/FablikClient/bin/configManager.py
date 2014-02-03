import os, logging
from logManager import LogManager

def getConfigPath():
    if os.name == 'posix':
        home = os.environ['HOME']
    else:
        home = os.environ['HOMEPATH']

    return os.path.join(home, '.fablik_client')


class Config:
    conf_file_name = getConfigPath()
    ismod = False

    #runtime variables
    SESSION_ID=''
    USER_NAME = ''
    USER_PASSWORD=None

    #config file saved variables
    BASE_SERIVICE_URL = ''
    WINDOWS_ORDERING = ''
    LANG_SID = ''
    LOG_LEVEL = logging.CRITICAL

    #constants
    FORM_CACHE_DIR = ''
    FORM_RUNTIME_DIR = ''
    MENU_CACHE = ''
    LANG_PATH = ''
    LOG_PATH = ''
    LANG_CONFIG = ''

    @classmethod
    def is_exists(cls):
        return os.path.exists(cls.conf_file_name)

    @classmethod
    def init_config(cls):
        cur_dir = os.path.abspath(os.path.curdir)
        cache_dir = os.path.join(cur_dir, 'cache')

        cls.MENU_CACHE = os.path.join(cache_dir, 'menu.cache')
        cls.LANG_PATH = os.path.join(cur_dir, 'lang')
        cls.LANG_CONFIG = os.path.join(cur_dir, 'lang/languages.conf')
        cls.FORM_CACHE_DIR =  cache_dir
        cls.FORM_RUNTIME_DIR = os.path.join(cur_dir, 'runtime')
        cls.LOG_PATH = os.path.join(cur_dir, 'logs')


    @classmethod
    def read_config(cls):
        #read config parameters from config file
        c_lines = open(cls.conf_file_name).readlines()

        config = []
        for line in c_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            config.append( line.split()[:2] )

        for c_param in config:
            if c_param[0] == 'SERVICE_URL':
                cls.BASE_SERIVICE_URL = c_param[1]
            elif c_param[0] == 'WINDOWS_ORDERING':
                cls.WINDOWS_ORDERING = c_param[1]
            elif c_param[0] == 'LANG_SID':
                cls.LANG_SID = c_param[1]
            elif c_param[0] == 'LOG_LEVEL':
                cls.LOG_LEVEL = int(c_param[1])
            elif c_param[0] == 'LAST_USER':
                cls.USER_NAME = c_param[1]
            else:
                raise Exception('Configuration parameter %s is not supported' % c_param[0])

        LogManager.init_log(cls.LOG_PATH, cls.LOG_LEVEL)

    @classmethod
    def save_config(cls):
        if not cls.ismod:
            return False

        f = open(cls.conf_file_name,'w')
        f.write('SERVICE_URL  %s\n' % cls.BASE_SERIVICE_URL)
        if cls.WINDOWS_ORDERING:
            f.write('WINDOWS_ORDERING  %s\n' % cls.WINDOWS_ORDERING)
        f.write('LANG_SID %s\n' % cls.LANG_SID)
        f.write('LOG_LEVEL %i\n' % cls.LOG_LEVEL)
        f.write('LAST_USER %s\n' % cls.USER_NAME)
        f.close()

        cls.ismod = False

        return True

    @classmethod
    def setServiceUrl(cls, url):
        if url == cls.BASE_SERIVICE_URL:
            return

        cls.BASE_SERIVICE_URL = url
        cls.ismod = True

    @classmethod
    def getServiceUrl(cls):
        return cls.BASE_SERIVICE_URL

    @classmethod
    def setWindowsOrdering(cls, value):
        if cls.WINDOWS_ORDERING == value:
            return

        if value not in ['cascade','tile']:
            raise Exception ('Windows ordering state must be cascade or tile!')

        cls.WINDOWS_ORDERING = value
        cls.ismod = True

    @classmethod
    def getWindowsOrdering(cls):
        return cls.WINDOWS_ORDERING

    @classmethod
    def getLangSid(cls):
        return cls.LANG_SID

    @classmethod
    def setLangSid(cls, lang_sid):
        if cls.LANG_SID == lang_sid:
            return

        cls.LANG_SID = lang_sid
        cls.ismod = True

    @classmethod
    def getLangConfig(cls):
        return cls.LANG_CONFIG

    @classmethod
    def getLangPath(cls):
        return cls.LANG_PATH

    @classmethod
    def getFormCacheDir(cls):
        return cls.FORM_CACHE_DIR

    @classmethod
    def getFormRuntimeDir(cls):
        return cls.FORM_RUNTIME_DIR

    @classmethod
    def getSessionID(cls):
        return cls.SESSION_ID

    @classmethod
    def setSessionID(cls, sessionID):
        cls.SESSION_ID = sessionID

    @classmethod
    def setLogLevel(cls, log_level):
        if log_level not in [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            raise Exception ('Unsupported log level: %s'%log_level)

        cls.LOG_LEVEL = log_level
        LogManager.change_log_level(log_level)

        cls.ismod = True

    @classmethod
    def getLogLevel(cls):
        return cls.LOG_LEVEL

