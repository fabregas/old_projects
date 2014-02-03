BEGIN;

CREATE TABLE bf_object_log
(
    table_name character varying(50) NOT NULL,
    operation_type character varying(10) NOT NULL,
    datetime timestamp without time zone NOT NULL,
    sql_statement text NOT NULL,
    object_id integer[] NOT NULL
);

--bf_objects_savepoint table is used on development environment for fixing versions (sprints)
--          and on production environment for fixing installation points.
CREATE TABLE bf_objects_savepoint (
  point_name character varying(128) NOT NULL,
  point_datetime timestamp without time zone NOT NULL,
  description character varying(1024) NOT NULL
);


CREATE LANGUAGE plpythonu;

CREATE OR REPLACE FUNCTION append_to_objectlog () RETURNS trigger AS $BODY$
	table = TD['table_name']
	
	attributes = plpy.execute("SELECT attname FROM pg_attribute \
		WHERE attrelid = (SELECT oid from pg_class WHERE relname = '%s') \
		AND attnum>0  AND atttypid<>0;" % table)
	attributes = [attr['attname'] for attr in attributes]

	primary_keys = plpy.execute("SELECT pg_attribute.attname \
			FROM pg_class, pg_index, pg_attribute \
			WHERE pg_attribute.attnum= any(pg_index.indkey) AND \
			pg_attribute.attrelid = pg_class.oid AND \
			pg_class.oid = pg_index.indrelid AND  \
			pg_class.relname = '%s' AND  \
			pg_index.indisprimary = 't';"% table)
	prime_keys = [attr['attname'] for attr in primary_keys]

	row_values = []

	if TD['event'] != 'DELETE':
		for akey in attributes:
			attr_val = TD['new'][akey]
			if attr_val is not None:
				row_values.append("''%s''" % attr_val)
			else:
				row_values.append("NULL")

	obj = TD['new']
	sql_statement = ''
	if TD['event'] == 'INSERT':
		sql_statement = 'INSERT INTO %s (%s) VALUES (%s);' %(table, ', '.join(attributes), ', '.join(row_values))
	elif TD['event'] == 'UPDATE':
		set_fields = ', '.join( ['%s = %s'%(attr,row_values[i]) for i,attr in enumerate(attributes)] )
		where_fields = ' AND '.join( ['%s = %s'%(pkey,TD['old'][pkey]) for pkey in prime_keys] )
		
		sql_statement = 'UPDATE %s SET %s WHERE %s;' % (table, set_fields, where_fields)
	else:
		where_fields = ' AND '.join( ['%s = %s'%(pkey,TD['old'][pkey]) for pkey in prime_keys] )
		sql_statement = 'DELETE FROM %s WHERE %s;' % (table, where_fields)
		obj = TD['old']

	plpy.execute("INSERT INTO bf_object_log (table_name, object_id, operation_type, datetime, sql_statement) \
		VALUES ('%s','{%s}','%s',now(),'%s')" % (table,
		', '.join([str(obj[pkey]) for pkey in prime_keys]),
		TD['event'],
		sql_statement)
	)
$BODY$ LANGUAGE 'plpythonu';


CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_audittype FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_departmentdisablerole FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_form FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_formpermission FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_group FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_grouprole FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_language FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_menurole FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_sql_query FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_sql_filter FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_sql_result FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_translate FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_translateobject FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_usergroup FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_audit FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_auditobject FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_department FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_role FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_menu FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();
CREATE TRIGGER append_objectlog_trigger BEFORE INSERT OR UPDATE OR DELETE ON bf_applicationinterface FOR EACH ROW EXECUTE PROCEDURE append_to_objectlog();

COMMIT;