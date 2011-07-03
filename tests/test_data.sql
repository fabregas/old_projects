BEGIN;
INSERT INTO NM_ROLE (id, role_sid, role_name) VALUES (1, 'admin','Admin role');
INSERT INTO NM_ROLE (id, role_sid, role_name) VALUES (2, 'readonly','Read only role');

INSERT INTO NM_USER (id, name, password_hash) VALUES (1, 'fabregas','');

INSERT INTO NM_USER_ROLE (user_id, role_id) VALUES (1,1);

INSERT INTO NM_CLUSTER_TYPE (id, type_sid) VALUES (1,'COMMON');
INSERT INTO NM_NODE_TYPE (id, type_sid) VALUES (1,'COMMON');

INSERT INTO NM_CLUSTER (id, cluster_sid, cluster_type, cluster_name, status, last_modifier_id) VALUES (1,'TEST_CLUSTER', 1, 'Test Cluster', 0, 1);
INSERT INTO NM_NODE (id, cluster_id, node_type, hostname, logic_name, status,last_datestart,login,password,last_modifier_id) VALUES (1,1,1,'127.0.0.1','test_node_1', 0, now(), 'test', 'test_pwd', 1);

INSERT INTO NM_OPERATION (id, name, timeout) VALUES (1, 'COMMON_OPERATION', 5);
INSERT INTO NM_OPERATION (id, name, timeout, node_type_id) VALUES (2, 'TEST_OPERATION', 2, 1);

INSERT INTO NM_OPERATION_INSTANCE (id, operation_id, initiator_id, start_datetime, status) VALUES (4444, 1,1,now(),0);
INSERT INTO NM_OPERATION_PROGRESS (node_id, instance_id, progress) VALUES ( 1, 4444, 0);

COMMIT;
