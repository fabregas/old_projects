import base64,os, hashlib
import psycopg2 as psycopg

def deploy_to_db(db_conn_string, form_archive):
    ret_code, ret_msg = 0, 'OK'
    db_conn = None
    try:
        f = open(form_archive,'rb')
        form_source = f.read()
        f.close()

        md5 = hashlib.md5()
        md5.update(form_source)
        checksum = md5.hexdigest()

        encSource = base64.encodestring(form_source)

        bname = os.path.basename(form_archive)
        bname = bname[:-4]
        formName = bname[:bname.find('_')]
        formVer = bname[bname.find('_')+1:]

        db_conn = psycopg.connect(db_conn_string)

        curs = db_conn.cursor()

        curs.execute("SELECT id FROM bf_form WHERE status=1 and name='%s'"%formName)
        oldID = curs.fetchone()

        curs.execute("UPDATE bf_form SET status=0 WHERE name='%s'"%(formName))
        curs.execute("SELECT id FROM bf_form WHERE checksum='%s'" % checksum)
        ret = curs.fetchone()
        if ret:
            curs.execute("UPDATE bf_form SET status=1 WHERE checksum='%s'"%(checksum))
        else:
            curs.execute("INSERT INTO bf_form (name, version, status, checksum, form_source) VALUES ('%s','%s', 1,'%s','%s');"%(formName,formVer,checksum,encSource))
            curs.execute("SELECT id FROM bf_form WHERE status=1 and name='%s'" % formName)
            newID = curs.fetchone()
            if oldID:
                curs.execute("UPDATE bf_formpermission SET form_id =%i where form_id=%i" % (newID[0], oldID[0]))

        db_conn.commit()
    except Exception, err:
        ret_code,ret_msg = -1, 'Fail: %s' % err
        if db_conn:
            db_conn.rollback()
    finally:
        if db_conn and not db_conn.closed:
            db_conn.close()


    return ret_code, ret_msg


def test_db_connection(db_conn_string):
    ret_code, ret_msg = 0, 'OK'
    try:
        db_conn = psycopg.connect(db_conn_string)
        db_conn.close()
    except Exception, err:
        ret_code,ret_msg = -1, 'Fail: %s' % err

    return ret_code, ret_msg


