import os
import ConfigParser
from ConfigParser import RawConfigParser

CONF_DIR = '/opt/blik/conf'

def getConfigFilePath():
    return os.path.join(CONF_DIR, 'blik_cloud_manager.conf')

class Config:
    @staticmethod
    def init():
        try:
            config_file = getConfigFilePath()
            if not os.path.exists(config_file):
                Config.createDefaults()

            config = RawConfigParser()
            config.read(config_file)

            Config.log_level = config.get('LOG','log_level')

            Config.db_host = config.get('DATABASE','host')
            Config.db_port = config.get('DATABASE','port')
            Config.db_user = config.get('DATABASE','user')
            Config.db_password = config.get('DATABASE','password')
            Config.db_name = config.get('DATABASE','database_name')

            Config.oper_callers_count = int(config.get('FRI', 'oper_callers_count'))
            Config.oper_results_threads = int(config.get('FRI', 'oper_results_threads'))
            Config.monitor_workers_count = int(config.get('FRI', 'monitor_workers_count'))
            Config.nodes_monitor_timeout = int(config.get('FRI', 'monitor_timeout'))
            Config.monitor_wait_response_timeout = int(config.get('FRI', 'monitor_wait_response_timeout'))
        except ConfigParser.NoOptionError, msg:
            raise Exception('ConfigParser. No option error: %s' % msg)
        except ConfigParser.Error, msg:
            raise Exception('ConfigParser: %s' % msg)

    @staticmethod
    def createDefaults():
        config = RawConfigParser()
        config.add_section('DATABASE')
        config.add_section('FRI')
        config.add_section('LOG')

        config.set('LOG', 'log_level', 'INFO')

        config.set('DATABASE', 'host', '127.0.0.1')
        config.set('DATABASE', 'port', '5432')
        config.set('DATABASE', 'user', 'postgres')
        config.set('DATABASE', 'password', '')
        config.set('DATABASE', 'database_name', 'blik_cloud_db')

        config.set('FRI', 'oper_callers_count', '3') #TODO: may be FRI parameters calculate automatically?
        config.set('FRI', 'oper_results_threads', '5')
        config.set('FRI', 'monitor_workers_count', '3')
        config.set('FRI', 'monitor_timeout', '60')
        config.set('FRI', 'monitor_wait_response_timeout', '5')

        config_file = getConfigFilePath()
        f = open(config_file, 'w')
        config.write(f)
        f.close()

    @staticmethod
    def getDatabaseConnectString():
        conn_str = 'host=%s user=%s port=%s dbname=%s'%(Config.db_host, Config.db_user, Config.db_port, Config.db_name)

        if Config.db_password:
            conn_str += ' password=%s' % Config.db_password

        return conn_str

Config.init()

