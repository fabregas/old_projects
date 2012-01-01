from setuptools import setup
import sys
from version import VERSION

setup(
    name = "NodeAgent",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "kksstt@gmail.com",
    description = "Node agent for Blik Cloud management system",
    packages = ['blik.nodeAgent', 'blik.nodeAgent.plugins'],  # include all packages under src
    scripts = ['bin/nodeAgent'],
    license = 'GPLv3',
    zip_safe = True
)

