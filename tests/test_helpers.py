
import io
import unittest


from parser import BitConsumer

class BitConsumerTestCase(unittest.TestCase):

    def test_simple(self):
        bc = BitConsumer(io.BytesIO(b"\xff"))
        v = bc.get(5)
        self.assertEqual(v, 0x1f)

    def test_get_from_left(self):
        bc = BitConsumer(io.BytesIO(b"\xf0"))
        v = bc.get(6)
        self.assertEqual(v, 0b111100)

    def test_exact(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.get(16)
        self.assertEqual(v, 0b1111000011110000)

    def test_exact_limit_prev(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.get(15)
        self.assertEqual(v, 0b111100001111000)

    def test_exact_limit_next(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0\xf0"))
        v = bc.get(17)
        self.assertEqual(v, 0b11110000111100001)

    def test_big(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0"))
        v = bc.get(12)
        self.assertEqual(v, 0b111100001111)

    def test_multiple(self):
        bc = BitConsumer(io.BytesIO(b"\xf0\xf0"))
        self.assertEqual(bc.get(3), 0b111)
        self.assertEqual(bc.get(2), 0b10)
        self.assertEqual(bc.get(1), 0b0)
        self.assertEqual(bc.get(5), 0b00111)
        self.assertEqual(bc.get(3), 0b100)
        self.assertEqual(bc.get(2), 0b00)

    def test_short_bin(self):
        bc = BitConsumer(io.BytesIO(b"\x01"))
        self.assertEqual(bc.get(4), 0)
        self.assertEqual(bc.get(4), 1)

    def test_no_bits(self):
        bc = BitConsumer(io.BytesIO(b"\x01"))
        self.assertEqual(bc.get(0), None)  # get 0!!
