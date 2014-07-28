# Copyright 2013-2014 Facundo Batista
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

"""Some helpers for the SWF parser."""

import itertools
import struct


def grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    This is taken from the itertools docs.
    """
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def unpack_si16(src):
    """Read and unpack signed integer 16b."""
    return struct.unpack("<h", src.read(2))[0]


def unpack_ui8(src):
    """Read and unpack unsigned integer 8b."""
    return struct.unpack("<B", src.read(1))[0]


def unpack_ui16(src):
    """Read and unpack unsigned integer 16b."""
    return struct.unpack("<H", src.read(2))[0]


def unpack_ui32(src):
    """Read and unpack unsigned integer 32b."""
    return struct.unpack("<I", src.read(4))[0]


def unpack_fixed8(src):
    """Get a FIXED8 value."""
    dec_part = unpack_ui8(src)
    int_part = unpack_ui8(src)
    return int_part + dec_part / 256


def unpack_fixed16(src):
    """Get a FIXED16 value (called plainly FIXED in the spec)."""
    dec_part = unpack_ui16(src)
    int_part = unpack_ui16(src)
    return int_part + dec_part / 65536


def unpack_float16(src):
    """Read and unpack a 16b float.

    The structure is:
    - 1 bit for the sign
    . 5 bits for the exponent, with an exponent bias of 16
    - 10 bits for the mantissa
    """
    bc = BitConsumer(src)
    sign = bc.u_get(1)
    exponent = bc.u_get(5)
    mantissa = bc.u_get(10)
    exponent -= 16
    mantissa /= 2 ** 10
    num = (-1 ** sign) * mantissa * (10 ** exponent)
    return num


def unpack_float(src):
    """Read and unpack a 32b float."""
    return struct.unpack("<f", src.read(4))[0]


def unpack_double(src):
    """Read and unpack a 64b float."""
    return struct.unpack("<d", src.read(8))[0]


class BitConsumer:
    """Get a byte source, yield bunch of bits."""
    def __init__(self, src):
        self.src = src
        self._bits = None
        self._count = 0

    def u_get(self, quant):
        """Return a number using the given quantity of unsigned bits."""
        if not quant:
            return
        bits = []
        while quant:
            if self._count == 0:
                byte = self.src.read(1)
                number = struct.unpack("<B", byte)[0]
                self._bits = bin(number)[2:].zfill(8)
                self._count = 8
            if quant > self._count:
                self._count, quant, toget = 0, quant - self._count, self._count
            else:
                self._count, quant, toget = self._count - quant, 0, quant
            read, self._bits = self._bits[:toget], self._bits[toget:]
            bits.append(read)
        data = int("".join(bits), 2)
        return data

    def s_get(self, quant):
        """Return a number using the given quantity of signed bits."""
        if quant == 1:
            # special case, just return that unsigned value
            return self.u_get(1)

        sign = self.u_get(1)
        raw_number = self.u_get(quant - 1)
        if sign == 0:
            # positive, simplest case
            number = raw_number
        else:
            # negative, complemento a 2
            complement = 2 ** (quant - 1) - 1
            number = -1 * ((raw_number ^ complement) + 1)
        return number


class ReadQuantityController:
    """A context manager that will complain if bad quantity is read."""
    def __init__(self, src, should):
        self._src = src
        self._should = should
        self._started = None

    def __enter__(self):
        """Enter the guarded block."""
        self._started = self._src.tell()

    def __exit__(self, *exc):
        """Exit the guarded block."""
        cur_pos = self._src.tell()
        if cur_pos != self._started + self._should:
            t = "Bad reading quantity: started={} should={} ended={}".format(
                self._started, self._should, cur_pos)
            raise ValueError(t)
