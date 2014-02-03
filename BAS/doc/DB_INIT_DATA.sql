BEGIN;

INSERT INTO bas_role (role_sid,role_name) VALUES ('topology_read', 'Topology view');
INSERT INTO bas_role (role_sid,role_name) VALUES ('topology_modify', 'Topology modify');
INSERT INTO bas_role (role_sid,role_name) VALUES ('topology_admin', 'Topology admin');
INSERT INTO bas_role (role_sid,role_name) VALUES ('app_read', 'Applications view');
INSERT INTO bas_role (role_sid,role_name) VALUES ('app_deploy', 'Applications deploy');
INSERT INTO bas_role (role_sid,role_name) VALUES ('app_admin', 'Applications admin');
INSERT INTO bas_role (role_sid,role_name) VALUES ('users_read', 'Users view');
INSERT INTO bas_role (role_sid,role_name) VALUES ('users_admin', 'Users admin');

INSERT INTO bas_user (name, password_md5) VALUES ('bas_node_agent','26c01dbc175433723c0f3ad4d5812948'); 
INSERT INTO bas_user (name, password_md5) VALUES ('root','26c01dbc175433723c0f3ad4d5812948'); 

INSERT INTO bas_user_roles (user_id, role_id) VALUES (1,1);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (1,5);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (1,6);                                                     


INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,1);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,2);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,3);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,4);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,5);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,6);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,7);                                                     
INSERT INTO bas_user_roles (user_id, role_id) VALUES (2,8);                                                     


INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (0, 'bas_username',1,'bas_node_agent');
INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (0, 'bas_password',4,'blik');
/*DELETE FOR PRODUCTION, CREATE OVER BAS CONSOLE
INSERT INTO BAS_CLUSTER (id,cluster_name, cluster_sid) VALUES (1,'Testing cluster N1','CLUSTER_01');
INSERT INTO BAS_CLUSTER_NODE (cluster_id, hostname, logic_name, datestart) VALUES (1, '192.168.80.83','first_node','2009-10-19 10:23:54');
INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (1, 'http_port',2,'33333');
INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (1, 'ssl_port',2,'6565');
INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (1, 'log_write_timeout',2,'3');
INSERT INTO BAS_CONFIG (config_object_id, param_name, param_type, param_value) VALUES (1, 'system_transport',1,'HTTP');
*/

COMMIT;
