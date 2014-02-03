# -*- coding: utf-8 -*-

sql_insert_to_msglog = "INSERT INTO BAS_APP_MESSAGE (method_id, node_id, sender_host, message_type, datetime, message) VALUES (%i, %i, '%s', %i,'%s','%s')"

sql_insert_to_statlog = "INSERT INTO BAS_APP_STATISTIC (app_id, node_id, write_datetime, in_count, out_count, err_count) VALUES (%i, %i,'%s', '%i', '%i', '%i')"

sql_get_all_cluster_nodes = "SELECT id,hostname FROM BAS_CLUSTER_NODE WHERE cluster_id=%i;"
sql_get_all_cluster_applications = "SELECT id FROM BAS_APPLICATION WHERE cluster_id=%i and active_flag=1 and app_type='native_app';"
sql_get_application = 'SELECT id,app_name,app_version,control_flag,active_flag,execute_code FROM BAS_APPLICATION WHERE id=%i;'
sql_get_app_by_version = "SELECT id FROM BAS_APPLICATION WHERE cluster_id=%i and app_name='%s' and app_version='%s';"
sql_get_active_app = "SELECT id FROM BAS_APPLICATION WHERE  cluster_id=%i and app_name='%s' and active_flag=1;"

sql_get_shared_libraries = "SELECT id FROM BAS_APPLICATION WHERE cluster_id=%i and active_flag=1 and app_type='shared_lib';"

sql_get_app_methods = "SELECT method_name,status,method_id FROM BAS_APP_METHOD WHERE application_id=%i"

sql_get_global_config = "SELECT param_name, param_value, param_type FROM BAS_CONFIG WHERE config_object_id=%i AND config_type=2;"
sql_get_app_config = "SELECT param_name, param_value, param_type FROM BAS_CONFIG WHERE config_object_id=%i AND config_type=3;"
sql_get_system_config = "SELECT param_name, param_value, param_type FROM BAS_CONFIG WHERE (config_object_id=%i OR config_object_id=0) AND config_type=1;"

sql_get_node = "SELECT cluster_id, id, hostname FROM BAS_CLUSTER_NODE WHERE logic_name='%s'"

sql_insert_log_message = "INSERT INTO BAS_LOG (node_id,msg_datetime,msg_level,log_message) VALUES (%i, '%s', %i, '%s')"

