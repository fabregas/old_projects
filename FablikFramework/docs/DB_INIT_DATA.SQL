BEGIN;

SELECT pg_catalog.setval('bf_applicationinterface_id_seq', 2, true);
SELECT pg_catalog.setval('bf_audit_id_seq', 14, true);
SELECT pg_catalog.setval('bf_audittype_id_seq', 1, true);
SELECT pg_catalog.setval('bf_condition_operation_id_seq', 1, false);
SELECT pg_catalog.setval('bf_department_id_seq', 18, true);
SELECT pg_catalog.setval('bf_form_id_seq', 1, false);
SELECT pg_catalog.setval('bf_group_id_seq', 10, true);
SELECT pg_catalog.setval('bf_language_id_seq', 1, true);
SELECT pg_catalog.setval('bf_menu_id_seq', 1, false);
SELECT pg_catalog.setval('bf_role_id_seq', 2, true);
SELECT pg_catalog.setval('bf_sql_filter_id_seq', 1, false);
SELECT pg_catalog.setval('bf_sql_query_id_seq', 1, false);
SELECT pg_catalog.setval('bf_sql_result_id_seq', 1, false);
SELECT pg_catalog.setval('bf_translate_id_seq', 1, false);
SELECT pg_catalog.setval('bf_translateobject_id_seq', 1, false);
SELECT pg_catalog.setval('bf_user_id_seq', 2, true);

INSERT INTO bf_department (id, symbol_id, name, description, parent_id) VALUES (1, 'RootDepartment', 'Root department', '', NULL);

INSERT INTO bf_user (id, department_id, status, login, name, password_checksum) VALUES (1, 1, 1, 'fabregas','fabregas', '26c01dbc175433723c0f3ad4d5812948');

INSERT INTO bf_applicationinterface (id, sid, url, db_connect_string, description) VALUES (1, 'FABLIK_BASE', NULL, 'host=127.0.0.1 user=postgres dbname=fablik_base', NULL);

INSERT INTO bf_applicationinterface (id, sid, url, db_connect_string, description) VALUES (2, 'FABLIK_QUERY', 'http://192.168.80.108:33333/FablikQueries/.wsdl', NULL, NULL);

INSERT INTO bf_auditobject (id, sid, name, description) VALUES (1, 'user', 'user', NULL);

INSERT INTO bf_role (id, sid, name, description) VALUES (1, 'mainAdmin', 'Main adminisrator', NULL);

INSERT INTO bf_role (id, sid, name, description) VALUES (2, 'regionAdmin', 'Regional administrator', NULL);

INSERT INTO bf_group (id, name, description, parent_id) VALUES (1, 'Administrator', 'Main administration group', NULL);

INSERT INTO bf_usergroup (user_id, group_id) VALUES (1,1);

INSERT INTO bf_grouprole (group_id, role_id) VALUES (1,1);

INSERT INTO bf_grouprole (group_id, role_id) VALUES (1,2);

INSERT INTO bf_language (id, lang_sid, lang_name) VALUES (1, 'English', 'English');

END;
