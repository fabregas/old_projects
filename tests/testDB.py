#!/usr/bin/python

import os
import sys
from blik.utils.config import Config

db_name = 'blik_cloud_db_test'
db_user = Config.db_user

Config.db_name = db_name

schema_file = './tests/cloud_db_schema.sql'
fixture_file = './tests/test_data.sql'

def createTestDB():
    os.system('dropdb -U %s %s'%(db_user, db_name))

    ret = os.system('createdb -U %s %s'%(db_user, db_name))
    if ret != 0:
        return False

    ret = os.system('psql -U %s -d %s -f %s'%(db_user, db_name, schema_file))
    if ret != 0:
        return False

    ret = os.system('psql -U %s -d %s -f %s'%(db_user, db_name, fixture_file))
    if ret != 0:
        return False

    return True


if __name__ == '__main__':
    print 'Generating test database...'
    ret = createTestDB()

    if ret:
        print '[OK] Test database generated successful!'
    else:
        print '[FAIL] Test database generation failed!'

    sys.exit(int(ret))
