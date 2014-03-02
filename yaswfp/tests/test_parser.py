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

"""Test cases for the parser."""

import io
import unittest

from unittest.mock import patch

from swfparser import SWFParser


class StructsTestCase(unittest.TestCase):
    """Tests for the different structs."""

    @patch.object(SWFParser, '_get_header')
    @patch.object(SWFParser, '_process_tags')
    def test_rect_simple(self, _a, _b):
        parser = SWFParser(io.BytesIO(b'\x1b\xae\x80'))
        self.assertEqual(parser._get_struct_rect(), (3, 5, 3, 5))

    @patch.object(SWFParser, '_get_header')
    @patch.object(SWFParser, '_process_tags')
    def test_rect_long(self, _a, _b):
        parser = SWFParser(io.BytesIO(b'\x70\x00\x0a\x8c\x00\x00\xda\xc0'))
        self.assertEqual(parser._get_struct_rect(), (0, 5400, 0, 7000))

    @patch.object(SWFParser, '_get_header')
    @patch.object(SWFParser, '_process_tags')
    def test_encodedu32_simple(self, _a, _b):
        parser = SWFParser(io.BytesIO(b'\x3a'))
        self.assertEqual(parser._get_struct_encodedu32(), 58)

    @patch.object(SWFParser, '_get_header')
    @patch.object(SWFParser, '_process_tags')
    def test_encodedu32_several(self, _a, _b):
        parser = SWFParser(io.BytesIO(b'\x8c\xac\x29'))
        # compose: 0101001 0101100 0001100
        self.assertEqual(parser._get_struct_encodedu32(), 677388)

    @patch.object(SWFParser, '_get_header')
    @patch.object(SWFParser, '_process_tags')
    def test_fixed8(self, _a, _b):
        parser = SWFParser(io.BytesIO(b'\x80\x07'))
        self.assertEqual(parser._get_struct_fixed8(), 7.5)
