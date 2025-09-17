# Copyright 2025 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-restclients-upass>`_.
"""

version_path = 'uw_admin_systems/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="UW-RestClients-UPass",
    version=VERSION,
    packages=["uw_admin_systems"],
    author="UW-IT SETS",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=["uw-restClients-core"],
    license="Apache License, Version 2.0",
    description=("A library for connecting to the Admin System API"),
    long_description=README,
    url="https://github.com/uw-it-aca/uw-restclients-upass",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)
