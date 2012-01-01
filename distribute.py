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
from build import build, TMP_DIR, RHEL_DISTR, DIST_DIR as LOCAL_DIST

DISTR_SERVER='root@blik-mirror'
#DISTR_SERVER='distributor@blik-mirror'

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


def distribute_rpm(pkg_name):
    remote_path = '%s:/repo/blik-products/' % DISTR_SERVER

    pkg_file, version = build(pkg_name, RHEL_DISTR)

    local_path = '%s/%s'% (LOCAL_DIST, pkg_file)

    print ('Copying package %s to %s'%(pkg_file,remote_path))
    ret = os.system('scp %s %s'%(local_path, remote_path))

    if ret:
        print ('ERROR: distribution package %s failed!'%pkg_name)
        sys.exit(1)


####################################################################


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print ('Usage: distribute.py <dist name> --gentoo | --rhel')
        sys.exit(1)

    dist_name = sys.argv[1]
    dist = sys.argv[2]

    if dist == '--gentoo':
        version = distribute_package(dist_name)
        distribute_portage(dist_name, version)

        mirror_updater = '/opt/blik/sbin/portage-mirror-update'
        ret = os.system('ssh %s %s /usr/portage/blik-products/%s/%s-%s.ebuild'%(DISTR_SERVER, mirror_updater, dist_name, dist_name, version))
        if ret:
            print ('ERROR! Mirror is not updated on distribution server')
            sys.exit(1)
    elif dist == '--rhel':
        distribute_rpm(dist_name)
        ret = os.system('ssh %s createrepo --update /repo/blik-products/'% DISTR_SERVER)
        if ret:
            print ('ERROR! Mirror is not updated on distribution server')
            sys.exit(1)
    else:
        print('--gentoo or --rhel option expected')
        sys.exit(2)


    print ('Package %s distributed successfully!'%dist_name)

