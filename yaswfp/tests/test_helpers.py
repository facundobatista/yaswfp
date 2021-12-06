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

"""Test cases for some helpers."""

import io
import unittest

from yaswfp.helpers import (
    BitConsumer,
    ReadQuantityController,
    unpack_ui8,
    unpack_ui32,
    unpack_fixed8,
)


class BitConsumerTestCase(unittest.TestCase):

    def test_simple(self):
        bc = BitConsumer(io.BytesIO(b"\xff"))
        v = bc.u_get(5)
        self.assertEqual(v, 0x1f)

    def test_get_from_left(self):
        bc = BitConsumer(io.BytesIO(b"\xf0"))
        v = bc.u_get(6)
        self.assertEqual(v, 0b111100)

    def test_exact(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.u_get(16)
        self.assertEqual(v, 0b1111000011110000)

    def test_exact_limit_prev(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.u_get(15)
        self.assertEqual(v, 0b111100001111000)

    def test_exact_limit_next(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.u_get(17)
        self.assertEqual(v, 0b11110000111100001)

    def test_big(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0"))
        v = bc.u_get(12)
        self.assertEqual(v, 0b111100001111)

    def test_multiple(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0"))
        self.assertEqual(bc.u_get(3), 0b111)
        self.assertEqual(bc.u_get(2), 0b10)
        self.assertEqual(bc.u_get(1), 0b0)
        self.assertEqual(bc.u_get(5), 0b00111)
        self.assertEqual(bc.u_get(3), 0b100)
        self.assertEqual(bc.u_get(2), 0b00)

    def test_short_bin(self):
        bc = BitConsumer(io.BytesIO(b"\x01"))
        self.assertEqual(bc.u_get(4), 0)
        self.assertEqual(bc.u_get(4), 1)

    def test_no_bits(self):
        bc = BitConsumer(io.BytesIO(b"\x01"))
        self.assertEqual(bc.u_get(0), 0)

    def test_signed(self):
        bc = BitConsumer(io.BytesIO(b"\x7b\xf8"))
        self.assertEqual(bc.s_get(0), 0)
        self.assertEqual(bc.s_get(4), 7)
        self.assertEqual(bc.s_get(10), -258)

    def test_fixedbit(self):
        bc = BitConsumer(io.BytesIO(b"\x70\xbb\xc3\xd7\x00"))
        self.assertEqual(bc.fb_get(17), 0.8807220458984375)
        self.assertEqual(bc.fb_get(16), -0.470001220703125)


class BitPacksTestCase(unittest.TestCase):
    """Check the structs unpacker."""

    def test_ui8(self):
        src = io.BytesIO(b'\x08')
        assert unpack_ui8(src) == 0x08

    def test_ui32(self):
        src = io.BytesIO(b'\x98\x19\x02\x00')
        assert unpack_ui32(src) == 137624

    def test_fixed8(self):
        src = io.BytesIO(b'\x80\x07')
        assert unpack_fixed8(src) == 7.5


class GuardedTestCase(unittest.TestCase):
    """Check the ReadQuantityController class."""

    def test_guarded_ok(self):
        src = io.BytesIO(b'abcde')
        with ReadQuantityController(src, 5):
            self.assertEqual(src.read(3), b'abc')
            self.assertEqual(src.read(2), b'de')

    def test_guarded_too_much(self):
        src = io.BytesIO(b'abcde')
        try:
            with ReadQuantityController(src, 4):
                src.read(5)
        except ValueError:
            pass
        else:
            self._fail("Should have failed")

    def test_guarded_too_little(self):
        src = io.BytesIO(b'abcde')
        try:
            with ReadQuantityController(src, 4):
                src.read(2)
        except ValueError:
            pass
        else:
            self._fail("Should have failed")
