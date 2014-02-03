#---FablikBaseLib---
get_lang = "SELECT id FROM BF_Language WHERE lang_sid = '%s'"
get_menu = '''
    SELECT DISTINCT ON (id) id, parent_id, form_sid,
    COALESCE((SELECT translation FROM BF_Translate WHERE object_id = bf_menu.id AND translate_obj = 1 AND lang_id=%(lang_id)i), bf_menu.name) m_name,
    COALESCE((SELECT translation FROM BF_Translate WHERE object_id = bf_menu.id AND translate_obj = 2 AND lang_id=%(lang_id)i), bf_menu.name) m_descr,
    shortcut
    FROM bf_menu, bf_menurole
    WHERE bf_menu.id = bf_menurole.menu_id
        AND bf_menurole.role_id IN (
            SELECT bf_role.id
            FROM bf_role, bf_user, bf_grouprole, bf_usergroup
            WHERE bf_role.id = bf_grouprole.role_id
            AND bf_grouprole.group_id = bf_usergroup.group_id
            AND bf_user.id = bf_usergroup.user_id
            AND (SELECT 1 from bf_departmentdisablerole
                WHERE department_id = bf_user.department_id
                AND role_id=bf_role.id) IS NULL
            AND bf_user.id = %(user_id)i
        )

'''

get_interfaces = "SELECT id, sid, url, description FROM bf_applicationInterface WHERE url IS NOT NULL OR url <> ''"
get_password_hash = "SELECT password_checksum,id FROM bf_user WHERE login = '%s'"
get_session = "SELECT session_guid FROM bf_activesession WHERE user_id=%i"
remove_session = "DELETE FROM bf_activesession WHERE session_guid='%s'"
get_session_by_id  = "SELECT user_id FROM bf_activesession WHERE session_guid='%s'"
modify_session = "UPDATE bf_activesession SET session_guid = '%s', session_start=current_timestamp WHERE user_id=%i"
insert_session = "INSERT INTO bf_activesession (session_guid, session_start, user_id) VALUES ('%s',current_timestamp,%i)"
remove_cursors  = "DELETE FROM bf_cursor WHERE session_guid = '%s'"

get_audittype = "SELECT id, sid, audit_level FROM bf_audittype"
get_objectstype = "SELECT id, sid FROM bf_auditobject"
insert_audit = "INSERT INTO bf_audit (object_type,object_id,audit_type,datetime,audit_message) VALUES (%i,%i,%i,current_timestamp,'%s')"
get_departments = "SELECT id,parent_id,name,sid,description FROM bf_department"
get_groups = "SELECT id,parent_id,name,description FROM bf_group"


#---FablikInterfaces---
get_interface_by_sid = "SELECT url,db_connect_string FROM bf_applicationInterface WHERE sid='%s'"
get_interface_by_id = "SELECT url,db_connect_string FROM bf_applicationInterface WHERE id=%i"

#forms
get_form_by_sid = "SELECT id FROM bf_form WHERE name='%s' AND status=1"
get_form_sid = "SELECT name FROM bf_form WHERE id=%i AND status=1"
get_form_perms = '''
    SELECT max(perm_type)
    FROM bf_FormPermission
    WHERE form_id=%i AND role_id IN (
        SELECT bf_role.id
        FROM bf_role, bf_user, bf_grouprole, bf_usergroup
        WHERE bf_role.id = bf_grouprole.role_id
        AND bf_grouprole.group_id = bf_usergroup.group_id
        AND bf_user.id = bf_usergroup.user_id
        AND (SELECT 1 from bf_departmentdisablerole
                WHERE department_id = bf_user.department_id
                AND role_id=bf_role.id) IS NULL
        AND bf_user.id = %i
    )
'''
check_form_checksum = "SELECT id FROM bf_form WHERE id=%i AND checksum='%s'"
get_form_source = "SELECT form_source FROM bf_form WHERE id=%i"

authorize = """
    SELECT count(r.id) 
    FROM bf_role r, bf_activesession s, bf_usergroup ug, bf_grouprole gr 
    WHERE s.session_guid='%s' AND ug.user_id=s.user_id 
        AND ug.group_id=gr.group_id AND gr.role_id=r.id AND r.sid='%s';
"""
