#!/usr/bin/python
import os
import shutil

DISKLESS_HOME = '/diskless'

os.system('rc-update add dhcpd default')
os.system('rc-update add named default')
os.system('rc-update add in.tftpd default')
os.system('rc-update add postgresql-9.0 default') #FIXME

#starting services
os.system('/etc/init.d/dhcpd restart')
os.system('/etc/init.d/named restart')
os.system('/etc/init.d/in.tftpd restart')

print 'Trying start postgresql server!'
ret = os.system('/etc/init.d/postgresql-9.0 restart')
if ret:
    print 'Postgresql is not started. May be it need configuration...'
    os.system('emerge --config postgresql-server')


pxe_cfg = os.path.join(DISKLESS_HOME,'pxelinux.cfg')
if not os.path.exists(pxe_cfg):
    os.makedirs(pxe_cfg)

shutil.copy('/etc/pxelinux/default', os.path.join(pxe_cfg, 'default'))

####################################
#database configuration
####################################

ret = os.system('createdb -U postgres  blik_cloud_db')
if not ret:
    os.system('psql -U postgres -d blik_cloud_db -f /opt/blik/db/cloud_db_schema.sql')
