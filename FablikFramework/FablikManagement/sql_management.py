
insert_department = "INSERT INTO bf_department (parent_id, symbol_id, name, description) VALUES (%s, '%s', '%s', '%s') RETURNING id"
update_department = "UPDATE bf_department SET parent_id=%s, symbol_id='%s', name='%s', description='%s' WHERE id=%s"
delete_department = "DELETE FROM bf_department WHERE id=%s"
check_department_sid = "SELECT 1 FROM bf_department WHERE symbol_id='%s' AND id!=%i"
get_child_count = "SELECT count(id) FROM bf_department WHERE parent_id=%i"
dep_users = "SELECT count(id) FROM bf_user WHERE department_id=%i"
remove_dep_roles = "DELETE FROM bf_departmentdisablerole WHERE department_id=%i"

insert_group = "INSERT INTO bf_group (parent_id, name, description) VALUES (%s, '%s', '%s') RETURNING id"
update_group = "UPDATE bf_group SET parent_id=%s, name='%s', description='%s' WHERE id=%s"
delete_group = "DELETE FROM bf_group WHERE id=%s"
remove_group_roles = "DELETE FROM bf_groupRole WHERE group_id=%s"
remove_group_users = "DELETE FROM bf_userGroup WHERE group_id=%s"
set_group_role = "INSERT INTO bf_grouprole (group_id, role_id) VALUES (%s, %s)"

insert_user = """INSERT INTO bf_user
                (login, password_checksum, name, email, birthday, description, department_id)
                VALUES ('%s','%s','%s','%s',%s,'%s',%s) RETURNING id"""
set_user_group = "INSERT INTO bf_userGroup VALUES (%s, %s)"
update_user = """UPDATE bf_user SET login='%s', name='%s',
                    email='%s', status=%s, birthday=%s, description='%s', department_id=%s WHERE id=%s"""
remove_user_groups = "DELETE FROM bf_userGroup WHERE user_id=%s"
remove_user_sessions = "DELETE FROM bf_activeSession WHERE user_id=%s"
delete_user = "DELETE FROM bf_user WHERE id=%s"
change_user_password = "UPDATE bf_user SET password_checksum='%s' WHERE id=%s"
