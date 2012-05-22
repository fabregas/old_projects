#!/usr/bin/python

import os
import sys
from blik.utils.config import Config

db_name = 'blik_cloud_db_test'
db_user = Config.db_user
Config.db_name = db_name

from blik.management.core import settings

from django.core.management import call_command

def createTestDB():
    print 'drop test database...'
    os.system('dropdb -U %s %s'%(db_user, db_name))
    print 'ok!'

    print 'create test database...'
    ret = os.system('createdb -U %s %s'%(db_user, db_name))
    if ret != 0:
        return False
    print 'ok!'

    settings.INSTALLED_APPS = ['blik.management.core']
    call_command('syncdb')

    return True


if __name__ == '__main__':
    print 'Generating test database...'
    ret = createTestDB()

    if ret:
        print '[OK] Test database generated successful!'
    else:
        print '[FAIL] Test database generation failed!'

    sys.exit(int(ret))
