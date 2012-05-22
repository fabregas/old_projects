from setuptools import setup
import sys
from version import VERSION

setup(
    name = "BlikDevel",
    version = VERSION,
    maintainer = "Konstantin Andrusenko",
    maintainer_email = "blikproject@gmail.com",
    description = "Development utilities for Blik products",
    packages = [],  # include all packages under src
    scripts = ['devel/cm-package'],
    license = 'GPLv3',
    data_files = [('/opt/blik/develop/spec/mgmt/gentoo_dist/', ['devel/spec/mgmt/gentoo_dist/package.ebuild']),
                    ('/opt/blik/develop/spec/node/gentoo_dist/', ['devel/spec/node/gentoo_dist/package.ebuild'])],
    zip_safe = True
)

