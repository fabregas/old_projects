#!/usr/bin/python
import os
import sys
import shutil
from blik.utils.exec_command import run_command


DISKLESS_HOME = '/opt/blik/diskless'
DISKLESS_GL_HOME = '/opt/blik/diskless_data'

if not os.path.exists(DISKLESS_HOME):
    os.makedirs(DISKLESS_HOME)
if not os.path.exists(DISKLESS_GL_HOME):
    os.makedirs(DISKLESS_GL_HOME)


#starting services
os.system('/etc/init.d/dhcpd restart')
os.system('/etc/init.d/named restart')
os.system('/etc/init.d/in.tftpd restart')
os.system('/etc/init.d/glusterfsd start')
os.system('/etc/init.d/boot-event-listener stop')
os.system('/etc/init.d/syslog-ng stop')
os.system('/etc/init.d/postgresql-9.0 restart')
os.system('/etc/init.d/syslog-ng start')
os.system('/etc/init.d/boot-event-listener start')

####################################
# Glusterfs share mounting
####################################
#run_command(['glusterfs', DISKLESS_HOME])

####################################
#database configuration
####################################

ret,out,err = run_command(['createdb', '-U',  'postgres',  'blik_cloud_db'])
if not ret:
    ret,out,err = run_command(['psql', '-U', 'postgres', '-d', 'blik_cloud_db', '-f', '/opt/blik/db/cloud_db_schema.sql'])
    if ret:
        print (err)
        sys.exit(1)

    ret,out,err = run_command(['psql', '-U', 'postgres', '-d', 'blik_cloud_db', '-f', '/opt/blik/db/logs_schema.sql'])
    if ret:
        print (err)
        sys.exit(1)


if len(sys.argv) > 1 and sys.argv[1] == '--skip-images':
    print ('Skiping images recreation...')
    sys.exit(0)

######################################
#canonical images and kernels install
######################################

ret = os.system('cp /usr/share/syslinux/pxelinux.0 %s'%DISKLESS_HOME)
if ret:
    sys.exit(1)

IMAGES = '/usr/portage/distfiles'

INITRAMFS_DIR = os.path.join(DISKLESS_HOME, 'initramfs')
if not os.path.exists(INITRAMFS_DIR):
    os.makedirs(INITRAMFS_DIR)

ret = os.system('cp %s/initramfs-x86 %s'%(IMAGES,INITRAMFS_DIR))
if ret:
    sys.exit(1)

ret = os.system('cp %s/initramfs-x86_64 %s'%(IMAGES,INITRAMFS_DIR))
if ret:
    sys.exit(1)


x86_canonical_image = IMAGES + '/image_canonical_x86.tar.bz2'
x86_64_canonical_image = IMAGES + '/image_canonical_x86_64.tar.bz2'
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


##### DNS files configure #######

os.system('chown root:named /{etc,var}/bind /var/{run,log}/named /var/bind/{sec,pri,dyn}')
os.system('chown root:named /var/bind/named.cache /var/bind/pri/{127,localhost}.zone /etc/bind/{bind.keys,named.conf}')
os.system('chmod 0640 /var/bind/named.cache /var/bind/pri/*.zone /etc/bind/{bind.keys,named.conf}')
os.system('chmod 0750 /etc/bind /var/bind/pri')
os.system('chmod 0770 /var/{run,log}/named /var/bind/{,sec,dyn}')

#################################
