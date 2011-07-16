from setuptools import setup
import sys
from version import VERSION

setup(
    name = "BootManager",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "kksstt@gmail.com",
    description = "Blik cloud boot manager",
    packages = ['blik', 'blik.bootManager'],  # include all packages under src
    license = 'GPLv3',
    data_files = [('/etc/dhcp/', ['config/dhcpd.conf'])],
    zip_safe = True
)

