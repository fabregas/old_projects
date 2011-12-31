import os
import sys
from setuptools import setup
from version import VERSION

def get_files(path):
    data_files = []
    for root, dirs, files in os.walk(path):
        ret_files = []
        for file_name in files:
            ret_files.append(os.path.join(root, file_name))

        data_files.append((os.path.join('/opt', root), ret_files))

    return data_files


setup(
    name = "NodesManager",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "blikproject@gmail.com",
    description = "Nodes Manager module of Blik Cloud management system",
    packages = [ 'blik.nodesManager', 'blik.nodesManager.plugins', 'blik.console', 'blik.console.console_base'],  # include all packages under src
    scripts = ['bin/nodesManager','bin/call-operation', 'bin/consoleManager'],
    data_files = get_files('blik/console/templates') + get_files('blik/console/static') + get_files('blik/console/menu'),
    license = 'GPLv3',
    zip_safe = True
)

