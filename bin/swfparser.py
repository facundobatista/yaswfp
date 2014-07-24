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

"""Parse a SWF file and expose all its internals."""

import argparse

from yaswfp import swfparser


parser = argparse.ArgumentParser(
    description='Parse a SWF file and show all its internals')
parser.add_argument('filepath', help='the SWF file to parse')
parser.add_argument('-t', '--show-tags', action='store_true',
                    help='show the first level tags of the file')
parser.add_argument('-e', '--extended', action='store_true',
                    help='show all objects with full detail and nested')
parser.add_argument('-c', '--coverage', action='store_true',
                    help='indicate a percentage of coverage of given file')
args = parser.parse_args()

swf = swfparser.parsefile(args.filepath)
print(swf.header)
print("Tags count:", len(swf.tags))

if args.coverage:
    swf.coverage()

if args.show_tags or args.extended:
    f = repr if args.extended else str
    for tag in swf.tags:
        print(f(tag))
