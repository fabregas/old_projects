#!/usr/bin/python
"""
Copyright (C) 2011 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package build.py
@author Konstantin Andrusenko
@date July 17, 2011

This script build packages for it distribution.
"""


import os, shutil, sys
import subprocess
import tarfile

DIST_DIR = './dist'
TMP_DIR = '/tmp'

def get_current_version():
    version = subprocess.Popen(['git', 'describe', '--always', '--tag', '--abbrev=0'], stdout=subprocess.PIPE).communicate()[0]
    version = version.strip()
    if len(version) == 0 or len(version) > 10:
        raise Exception('Project version is invalid!')

    log = subprocess.Popen(['git', 'log', '%s..HEAD'%version, '--format=%h'], stdout=subprocess.PIPE).communicate()[0]
    if log:
        revision = len(log.split('\n'))-1
    else:
        revision = 0

    if revision:
        return '%s-r%i'%(version, revision)
    return version


def make_tempdir(pkg_name):
    tmp_dir = '%s/%s' % (TMP_DIR,pkg_name)

    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)

    os.mkdir(tmp_dir)

    return tmp_dir

def __process_tree(dir_name, files):
    dir_cont = os.listdir(dir_name)

    for f in dir_cont:
        if f.startswith('.'):
            continue
        item = os.path.join(dir_name, f)
        if os.path.isdir(item):
            __process_tree(item, files)
        else:
            files.append(item)

def copy_dist(dist_name, tmp_dir):
    install_dir = './install/%s'%dist_name
    lines = open('%s/CONTENT'%install_dir).readlines()

    files = []
    for line in lines:
        line = line.strip()
        if (not line) or line.startswith('#'):
            continue

        dir_name = os.path.dirname(line)
        file_name = os.path.basename(line)

        if file_name == '*':
            __process_tree(dir_name, files)
        else:
            files.append(line)


    for file_path in files:
        dir_name = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)

        print('copying %s...'%file_path)
        dest_dir = os.path.join(tmp_dir, dir_name)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        shutil.copy(file_path, dest_dir)

    meta_dir = '%s/meta/'%install_dir
    files = os.listdir(meta_dir)
    for item in files:
        path = os.path.join(meta_dir, item)
        if os.path.isfile(path):
            print('copying %s...'%path)
            shutil.copy(path, tmp_dir)

def pack(pkg_name):
    out_file = '%s/%s.tar'%(DIST_DIR, pkg_name)

    if not os.path.exists(DIST_DIR):
        os.makedirs(DIST_DIR)

    tar = tarfile.TarFile(out_file,'w')

    cur_dir = os.path.abspath('.')
    os.chdir(os.path.join(TMP_DIR,pkg_name))
    content = os.listdir('.')
    for item in content:
        if item.startswith('.'):
            continue
        tar.add(item)
    tar.close()
    os.chdir(cur_dir)


def build(dist_name):
    version = get_current_version()
    pkg_name = '%s-%s'%(dist_name, version)

    tmp_dir = make_tempdir(pkg_name)

    f = open(os.path.join(tmp_dir, 'version.py'), 'w')
    f.write('VERSION="%s"'%version)
    f.close()

    copy_dist(dist_name, tmp_dir)
    pack(pkg_name)

    return '%s.tar' % pkg_name, version


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print ('Usage: build.py <dist name>')
        sys.exit(1)

    dist_name = sys.argv[1]

    pkg_name, ver = build(dist_name)

    print ('Package %s created successfully!'%pkg_name)
