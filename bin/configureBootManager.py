#!/usr/bin/python
import os
import shutil

DISKLESS_HOME = '/diskless'

os.system('rc-update add dhcpd default')
os.system('rc-update add named default')
os.system('rc-update add in.tftpd default')


pxe_cfg = os.path.join(DISKLESS_HOME,'pxelinux.cfg')
if not os.path.exists(pxe_cfg):
    os.makedirs(pxe_cfg)

shutil.copy('/etc/pxelinux/default', os.path.join(pxe_cfg, 'default'))
