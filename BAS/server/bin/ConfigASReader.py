# -*- coding: utf-8 -*-
import ConfigParser
from ConfigParser import RawConfigParser
from sql_queries import sql_get_system_config, sql_get_node
import Database
from Exceptions import Error
from settings import AS_NODE_NAME

SYS_CONFIG_PARAMETERS = ('http_port', 'ssl_port', 'log_write_timeout','system_transport','bas_username','bas_password')

class Config:
    def __init__(self, conf_file):
        try:
            config = RawConfigParser()
            config.read(conf_file)

            self.db_host = config.get('DB','host')
            self.db_port = config.get('DB','port')
            self.db_user = config.get('DB','user')
            self.db_password = config.get('DB','password')
            self.db_name = config.get('DB','database_name')
        except ConfigParser.NoOptionError, msg:
            raise Error(str(msg))
        except ConfigParser.Error, msg:
            raise Error(str(msg))

        try:
            database = Database.Database('host=%s user=%s dbname=%s port=%s password=%s' %
                        (self.db_host, self.db_user,self.db_name,self.db_port,self.db_password))

            cur_node = database.execute(sql_get_node % AS_NODE_NAME)

            if not cur_node:
                database.close()
                raise Error("Node with name *%s* is not found in database"% AS_NODE_NAME)

            self.as_host = cur_node[0][2]
            self.node_id = cur_node[0][1]
            self.cluster_id = cur_node[0][0]

            rets = database.execute(sql_get_system_config % self.cluster_id)

            parameters = []
            for conf in rets:
                #print conf[0],conf[1]
                param_name = conf[0].strip().lower()
                param_type = int(conf[2])
                param_val = conf[1].strip()
                parameters.append(param_name)

                if param_type in [1,4]: #string or hidden string
                    exec("self.%s = '%s'"%(param_name, param_val))

                elif param_type == 2: #integer
                    exec("self.%s = int(%s)"%(param_name, param_val))

                elif param_type == 3: #boolean
                    val = 0
                    if param_val.lower() == 'true':
                        val = 1

                    exec("self.%s = bool(%s)"%(param_name, val))
                else:
                    raise Exception('Configuration parameters *%s* has unknown type'%conf[0])

            for conf in SYS_CONFIG_PARAMETERS:
                if conf not in parameters:
                    raise Exception('Cluster configuration  parameter *%s* is not found in database'%conf)
        finally:
            try: database.close()
            except: pass

