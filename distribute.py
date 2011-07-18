#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package distribute.py
@author Konstantin Andrusenko
@date July 17, 2011

This script distribute Blik packages to Distribution Server.
"""
####################################################################

import sys, os, shutil
from build import build, TMP_DIR, DIST_DIR as LOCAL_DIST

DISTR_SERVER='root@192.168.56.103'
#DISTR_SERVER='distributor@distribution_server'

####################################################################

def distribute_package(pkg_name):
    remote_path = '%s:/usr/portage/distfiles' % DISTR_SERVER

    pkg_file, version = build(pkg_name)

    local_path = '%s/%s'% (LOCAL_DIST, pkg_file)

    print ('Copying package %s to %s'%(pkg_file,remote_path))
    ret = os.system('scp %s %s'%(local_path, remote_path))

    if ret:
        print ('ERROR: distribution package %s failed!'%pkg_name)
        sys.exit(1)

    return version


def prepare_ebuild(pkg_name, out_path, version):
    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    os.makedirs(out_path)

    ebuild = 'install/%s/gentoo_dist/ebuild'%pkg_name
    metadata = 'install/%s/gentoo_dist/metadata.xml'%pkg_name
    changelog = 'install/%s/gentoo_dist/ChangeLog'%pkg_name

    ret = os.system('cp %s %s/%s-%s.ebuild' % (ebuild,out_path,pkg_name,version))
    if ret:
        print ('ERROR!')
        sys.exit(1)

    if os.path.exists(metadata):
        os.system('cp %s %s/metadata.xml'%(metadata,out_path))

    if os.path.exists(changelog):
        os.system('cp %s %s/ChangeLog'%(changelog,out_path))


def distribute_portage(pkg_name, version):
    remote_path = '%s:/opt/blik/portage/blik-products/' % DISTR_SERVER

    prepare_ebuild(pkg_name, os.path.join(TMP_DIR,pkg_name), version)

    os.chdir(TMP_DIR)

    print ('Copy portage files to %s'%remote_path)
    ret = os.system('scp -r %s %s' % (pkg_name,remote_path))

    if ret:
        print ('ERROR: distribution package %s failed!'%pkg_name)
        sys.exit(1)

    return ret

####################################################################


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: distribute.py <dist name>')
        sys.exit(1)

    dist_name = sys.argv[1]

    version = distribute_package(dist_name)
    distribute_portage(dist_name, version)

    mirror_updater = '/opt/blik/sbin/portage-mirror-update'
    ret = os.system('ssh %s %s'%(DISTR_SERVER, mirror_updater))
    if ret:
        print ('ERROR! Mirror is not updated on distribution server')
        sys.exit(1)

    print ('Package %s distributed successfully!'%dist_name)

