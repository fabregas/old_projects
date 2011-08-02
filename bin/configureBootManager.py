#!/usr/bin/python
import os
import sys
import shutil

DISKLESS_HOME = '/opt/blik/diskless'

os.system('rc-update add ntpd default')
os.system('rc-update add dhcpd default')
os.system('rc-update add named default')
os.system('rc-update add in.tftpd default')
os.system('rc-update add glusterfsd default')
os.system('rc-update add postgresql-9.0 default') #FIXME

#starting services
os.system('/etc/init.d/dhcpd restart')
os.system('/etc/init.d/named restart')
os.system('/etc/init.d/in.tftpd restart')
os.system('/etc/init.d/glusterfsd restart')

#if not os.path.exists('/var/lib/postgresql/9.0/data'):
#    print 'Postgresql is not configured! Configuring...'
#    os.system('emerge --config postgresql-server')

print 'Trying start postgresql server!'
os.system('/etc/init.d/postgresql-9.0 restart')


####################################
#database configuration
####################################

ret = os.system('createdb -U postgres  blik_cloud_db > /dev/null')
if not ret:
    ret = os.system('psql -U postgres -d blik_cloud_db -f /opt/blik/db/cloud_db_schema.sql')
    if ret:
        sys.exit(1)

######################################
#canonical images and kernels install
######################################

if not os.path.exists(DISKLESS_HOME):
    os.makedirs(DISKLESS_HOME)
ret = os.system('cp /usr/share/syslinux/pxelinux.0 %s'%DISKLESS_HOME)
if ret:
    sys.exit(1)

IMAGES = 'ftp://blik-mirror/images/'

INITRAMFS_DIR = os.path.join(DISKLESS_HOME, 'initramfs')
if not os.path.exists(INITRAMFS_DIR):
    os.makedirs(INITRAMFS_DIR)

ret = os.system('wget %s -O %s/initramfs-x86'%(os.path.join(IMAGES, 'initramfs-x86'),INITRAMFS_DIR))
if ret:
    sys.exit(1)

ret = os.system('wget %s -O %s/initramfs-x86_64'%(os.path.join(IMAGES, 'initramfs-x86_64'),INITRAMFS_DIR))
if ret:
    sys.exit(1)


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

pxe_cfg = os.path.join(DISKLESS_HOME,'pxelinux.cfg')
if not os.path.exists(pxe_cfg):
    os.makedirs(pxe_cfg)

default_x86 = os.path.join(pxe_cfg, 'default-x86')
default = os.path.join(pxe_cfg, 'default')

if not os.path.exists(default):
    os.system('ln %s %s'%(default_x86, default))
#os.system('unlink %s'%default)


##### DNS files configure #######
#os.system('touch /etc/bind/pri/192.168.87.zone.jnl')
#os.system('touch /etc/bind/pri/blik.zone.jnl')

os.system('chown root:named /{etc,var}/bind /var/{run,log}/named /var/bind/{sec,pri,dyn}')
os.system('chown root:named /var/bind/named.cache /var/bind/pri/{127,localhost}.zone /etc/bind/{bind.keys,named.conf}')
os.system('chmod 0640 /var/bind/named.cache /var/bind/pri/*.zone /etc/bind/{bind.keys,named.conf}')
os.system('chmod 0750 /etc/bind /var/bind/pri')
os.system('chmod 0770 /var/{run,log}/named /var/bind/{,sec,dyn}')

#################################
