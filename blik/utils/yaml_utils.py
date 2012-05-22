#!/usr/bin/python
"""
Copyright (C) 2012 Konstantin Andrusenko
    See the documentation for further information on copyrights,
    or contact the author. All Rights Reserved.

@package blik.utils.yaml_utils
@author Konstantin Andrusenko
@date May 26, 2012

This module contains the YamlFile class implementation
for easy yaml file parsing and dumping...
"""

import os
import yaml

class YamlFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.objects = {}

    def parse(self):
        url_lower = self.file_path.lower()
        if url_lower.startswith('http://') or url_lower.startswith('ftp://'):
            yaml_file_out = tempfile.mktemp(prefix='yaml-spec')

            ret,out,err = run_command(['wget', self.file_path, '-O', yaml_file_out])
            if ret:
                raise RuntimeError('YAML file %s does not downloaded! Details: %s'%(self.file_path, err))
        else:
            if not os.path.exists(self.file_path):
                raise RuntimeError('YAML file %s does not found!'% self.file_path)

            yaml_file_out = self.file_path

        try:
            f_cont = open(yaml_file_out).read()
        except Exception, err:
            raise RuntimeError('YAML file %s does not read! Details: %s'% (self.file_path, err))

        try:
            self.objects = yaml.load(f_cont)
        except Exception, err:
            raise RuntimeError('YAML file %s is invalid! Details: %s'% (self.file_path, err))

    def validate(self, structure):
        pass

    def get_object(self, obj_name):
        if self.objects.has_key(obj_name):
            return self.objects[obj_name]

        raise RuntimeError('Object <%s> is not found in YAML file' % obj_name)

    def load_objects(self, objects):
        self.objects.update(objects)

    def save(self):
        yaml_str = yaml.dump(self.objects)
        open(self.file_path, 'w').write(yaml_str)

