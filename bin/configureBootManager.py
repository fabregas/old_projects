#!/usr/bin/python
import os
import shutil

DISKLESS_HOME = '/opt/blik/diskless'

os.system('rc-update add dhcpd default')
os.system('rc-update add named default')
os.system('rc-update add in.tftpd default')
os.system('rc-update add postgresql-9.0 default') #FIXME

#starting services
os.system('/etc/init.d/dhcpd restart')
os.system('/etc/init.d/named restart')
os.system('/etc/init.d/in.tftpd restart')

if not os.path.exists('/var/lib/postgresql/9.0/data'):
    print 'Postgresql is not configured! Configuring...'
    os.system('emerge --config postgresql-server')

print 'Trying start postgresql server!'
os.system('/etc/init.d/postgresql-9.0 restart')

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

######################################
#canonical images and kernels install
######################################

IMAGES = 'ftp://blik-products-distribution/images/'

x86_canonical_image = IMAGES + 'image_canonical_x86.tar.bz2'
x86_64_canonical_image = IMAGES + 'image_canonical_x86_64.tar.bz2'
default_node_yaml = '/opt/blik/conf/default_node.yaml'

ret = os.system('node-image-updater -t canonical -a x86 -i %s --dont-unpack'%x86_canonical_image)
if ret:
    sys.exit(1)


ret = os.system('node-image-updater -t canonical -a x86_64 -i %s --dont-unpack'%x86_64_canonical_image)
if ret:
    sys.exit(1)


ret = os.system('node-type-installer --skip-db %s'%default_node_yaml)
if ret:
    sys.exit(1)

