#!/usr/bin/env python3

# Copyright 2014 Facundo Batista
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further info, check  http://github.com/facundobatista/yaswfp

"""The setup."""

import os
from distutils.core import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


def _get_version():
    """Get the version from module itself."""
    with open("yaswfp/swfparser.py") as fh:
        for line in fh:
            if line.startswith("VERSION = "):
                return line.split("=")[-1].strip().strip('"')


setup(
    name='yaswfp',
    version=_get_version(),
    license='GPL-3',
    author='Facundo Batista',
    author_email='facundo@taniquetil.com.ar',
    description='Yet Another SWF Parser.',
    long_description=README,
    url='http://github.com/facundobatista/yaswfp',
    packages=['yaswfp'],
    scripts=["bin/swfparser"],
    package_data={
        '': ['COPYING', 'README.rst'],
    }
)
