from setuptools import setup
import sys
from version import VERSION

setup(
    name = "NodesManager",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "blikproject@gmail.com",
    description = "Nodes Manager module of Blik Cloud management system",
    packages = [ 'blik.nodesManager', 'blik.nodesManager.plugins'],  # include all packages under src
    scripts = ['bin/nodesManager'],
    license = 'GPLv3',
    zip_safe = True
)

