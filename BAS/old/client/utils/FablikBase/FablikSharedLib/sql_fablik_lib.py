
get_menu = 'SELECT id, parent_id, role_id, form_id, name, help_description, shortcut FROM bf_menu'
get_interfaces = 'SELECT id, sid, url, description FROM bf_applicationInterface'
get_password_hash = "SELECT password_checksum,id FROM bf_user WHERE login = '%s'"
get_session = "SELECT session_guid FROM bf_activesession WHERE user_id=%i"
get_session_by_id  = "SELECT user_id FROM bf_activesession WHERE session_guid='%s'"
modify_session = "UPDATE bf_activesession SET session_guid = '%s', session_start=current_timestamp WHERE user_id=%i"
insert_session = "INSERT INTO bf_activesession (session_guid, session_start, user_id) VALUES ('%s','%s',%i)"
get_user_roles = """
SELECT bf_role.id, bf_role.sid 
FROM bf_role, bf_user, bf_positionrole
WHERE bf_role.id = bf_positionrole.role_id
AND bf_positionrole.position_id = bf_user.position_id
AND (SELECT 1 from bf_departamentdisablerole 
    WHERE departament_id = bf_user.departament_id 
    AND role_id=bf_role.id) IS NULL
AND bf_user.id = %i
"""
get_audittype = "SELECT id, sid, audit_level FROM bf_audittype"
get_objectstype = "SELECT id, sid FROM bf_auditobject"
insert_audit = "INSERT INTO bf_audit (object_type,object_id,audit_type,datetime,audit_message) VALUES (%i,%i,%i,current_timestamp,'%s')"
get_departaments = "SELECT id,parent_id,name FROM bf_departament"
get_positions = "SELECT id,parent_id,name FROM bf_position"


insert_departament = "INSERT INTO bf_departament (parent_id,name,description) VALUES (%s,'%s','%s') RETURNING id"
update_departament = "UPDATE bf_departament SET parent_id=%s, name='%s',description='%s' WHERE id=%i'"
get_subdepartaments_count = "SELECT count(id) FROM bf_departament WHERE parent_id=%i"
delete_departament = "DELETE FROM bf_departament WHERE id=%i"

insert_position = "INSERT INTO bf_position (parent_id,name,description) VALUES (%s,'%s','%s') RETURNING id"
update_position = "UPDATE bf_position SET parent_id=%s, name='%s',description='%s' WHERE id=%i'"
get_subpositions_count = "SELECT count(id) FROM bf_position WHERE parent_id=%i"
delete_position = "DELETE FROM bf_position WHERE id=%i"
