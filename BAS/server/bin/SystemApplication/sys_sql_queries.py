
sql_get_app_by_version = "SELECT id FROM BAS_APPLICATION WHERE cluster_id=%i and app_name='%s' and app_version='%s';"
sql_check_user_role = '''
        SELECT b_user.id
        FROM BAS_USER_ROLES user_role, BAS_USER b_user, BAS_ROLE b_role
        WHERE b_user.name = '%s'
            AND b_user.id = user_role.user_id
            AND user_role.role_id = b_role.id
            AND b_role.role_sid='%s'
'''
sql_get_user_passwd = "SELECT password_md5 FROM BAS_USER WHERE id=%i;"
sql_get_active_app = "SELECT id FROM BAS_APPLICATION WHERE  cluster_id=%i and app_name='%s' and active_flag=1;"
sql_update_application = "UPDATE BAS_APPLICATION SET active_flag=0 WHERE cluster_id=%i and app_name='%s';"
sql_insert_application = "INSERT INTO BAS_APPLICATION (cluster_id, app_name,app_version,app_type,control_flag,deploy_datetime, active_flag, execute_code) VALUES (%i, '%s', '%s','%s',%i, '%s', 1,'%s');"

sql_update_config = "UPDATE bas_config SET config_object_id=%i WHERE config_type=3 and config_object_id=%i;"
sql_remove_app_config = "DELETE FROM BAS_CONFIG WHERE config_type=3 and config_object_id=%i"

sql_insert_app_method = "INSERT INTO BAS_APP_METHOD (application_id, method_name, status) VALUES (%i, '%s', 0)"
sql_remove_app_logs = "DELETE FROM BAS_APP_MESSAGE WHERE method_id IN (SELECT method_id FROM BAS_APP_METHOD WHERE application_id=%i)"
sql_remove_app_stats = "DELETE FROM BAS_APP_STATISTIC WHERE app_id=%i"
sql_get_next_active_app = "SELECT max(id) FROM BAS_APPLICATION WHERE app_name=(SELECT app_name FROM BAS_APPLICATION WHERE id=%i) AND id <> %i"
sql_remove_app_methods = "DELETE FROM BAS_APP_METHOD WHERE application_id=%i"
sql_remove_application = "DELETE FROM BAS_APPLICATION WHERE id=%i"

sql_get_application_type = "SELECT app_type FROM BAS_APPLICATION WHERE  id = %i"
sql_get_app_type_by_name = "SELECT app_type FROM BAS_APPLICATION WHERE cluster_id=%i and  app_name='%s' and active_flag=1"

sql_activate_application = "UPDATE bas_application SET active_flag=1 WHERE id=%i"
sql_get_application_by_id = "SELECT app_name,app_type FROM bas_application WHERE id=%i"
