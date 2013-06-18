
# ¡Py3!

import io
import itertools
import math
import struct
import sys
import zlib


# data types

def _get_bytes(src, length):
    """Return N bytes."""
    if isinstance(src, bytes):
        assert len(src) == length
    else:
        src = src.read(length)
    return src

def si8(src):
    """Signed integer 8b."""
    src = _get_bytes(src, 1)
    return struct.unpack("<b", src)[0]

def ui8(src):
    """Unsigned integer 8b."""
    src = _get_bytes(src, 1)
    return struct.unpack("<B", src)[0]

def si16(src):
    """Signed integer 16b."""
    src = _get_bytes(src, 2)
    return struct.unpack("<h", src)[0]

def ui16(src):
    """Unsigned integer 16b."""
    src = _get_bytes(src, 2)
    return struct.unpack("<H", src)[0]

def si32(src):
    """Signed integer 32b."""
    src = _get_bytes(src, 4)
    return struct.unpack("<i", src)[0]

def ui32(src):
    """Unsigned integer 32b."""
    src = _get_bytes(src, 4)
    return struct.unpack("<I", src)[0]

def _grouper(n, iterable, fillvalue=None):
    """Collect data into fixed-length chunks or blocks.

    This is taken from the itertools docs.
    """
    # grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)

def rect(src):
    """RECT structure."""
    firstbyte = ui8(src)
    nbits = firstbyte >> 3
    rest_len = math.ceil((5 + 4 * nbits) / 8) - 1  # already read first
    rest_bytes = src.read(rest_len)
    rest_ints = struct.unpack("<%dB" % (rest_len,), rest_bytes)
    allbins = (bin(firstbyte)[-3:] +
               ''.join((bin(i)[2:]).zfill(8) for i in rest_ints))
    groups = list(_grouper(nbits, allbins))
    return tuple(int(''.join(x), 2) for x in groups[:4])

def rgba(src):
    """RGBA structure."""
    return [ui8(src) for _ in range(4)]

def string(src):
    """STRING structure."""
    data = []
    while True:
        t = src.read(1)
        if t == b'\x00':
            break
        data.append(t)
    val = b''.join(data)
    return val.decode("utf8")


# handlers

def handle_definebits(data, ident):
    """Handle the DefineBits data."""
    character_id = ui16(data[:2])
    print(ident + "CharacterID:", character_id)
    assert data[2:4] == b'\xff\xd8'
    assert data[-2:] == b'\xff\xd9'
    jpegdata = data[2:]
    print(ident + "JPEGData:", len(jpegdata), jpegdata[:20])
    with open("image-%04d.jpeg" % (character_id,), 'wb') as fh:
        fh.write(jpegdata)


def _byte2bin(src):
    """Return a byte in a nice bin form."""
    b = ui8(src)
    t = bin(b)[2:]
    return t.zfill(8)


def _byte2flags(src, keys):
    """Convert a byte to a dict with keys as flags."""
    b = ui8(src)
    assert len(keys) == 8
    keys = keys[::-1]
    d = {}
    for k in keys:
        b, flag = divmod(b, 2)
        d[k] = bool(flag)
    return d


#def handle_definetext(data):
#    """Handle DefineText."""
#    src = io.BytesIO(data)
#    character_id = ui16(src)
#    print("  CharacterID:", character_id)
#    print("  TextBounds:", rect(src))
#    print("  TextMatrix:", matrix(src))
#    print("  GlyphBits:", ui8(src))
#    print("  AdvanceBits:", ui8(src))
#
#    # textrecords
#    while True:
#        tag_fb = ui16(fh)
#        tag_type = tag_fb >> 6
#        if tag_type == 0:
#            print("End.")
#            break
#        tag_len = tag_fb & 0x3f
#        if tag_len == 0x3f:
#            # the length is the next four bytes!
#            tag_len = si32(fh)
#        tag_payload = fh.read(tag_len)
#        if b"Este programa vuelve a emi" in tag_payload:
#            print("ASSSSSSSSSSSSSSSSSSDT")


def handle_defineedittext(data, ident):
    """Handle DefineEditText."""
    src = io.BytesIO(data)
    character_id = ui16(src)
    print(ident + "CharacterID:", character_id)
    print(ident + "Bounds:", rect(src))

    flags = {}
    flags.update(_byte2flags(src, "HasText WordWrap Multiline Password "
                                  "ReadOnly HasTextColor HasMaxLength "
                                  "HasFont".split()))
    flags.update(_byte2flags(src, "HasFontClass AutoSize HasLayout NoSelect "
                                  "Border WasStatic HTML UseOutlines".split()))
    print(ident + "Lot of flags:", flags)
    if flags['HasFont']:
        print(ident + "FontID:", ui16(src))
    if flags['HasFontClass']:
        print(ident + "FontClass:", string(src))
    if flags['HasFont']:
        print(ident + "FontHeight:", ui16(src))

    if flags['HasTextColor']:
        print(ident + "TextColor:", rgba(src))
    if flags['HasMaxLength']:
        print(ident + "MaxLength:", ui16(src))
    if flags['HasLayout']:
        print(ident + "Align:", ui8(src))
        print(ident + "LeftMargin:", ui16(src))
        print(ident + "RightMargin:", ui16(src))
        print(ident + "Indent:", ui16(src))
        print(ident + "Leading:", ui16(src))

    print(ident + "VariableName:", string(src))
    if flags["HasText"]:
        print(ident + "InitialText:", repr(string(src)))


def process_tags(fh, ident=''):
    """Process tags."""
    while True:
        tag_fb = ui16(fh)
        tag_type = tag_fb >> 6
        if tag_type == 0:
            print(ident + "End.")
            break
        tag_len = tag_fb & 0x3f
        if tag_len == 0x3f:
            # the length is the next four bytes!
            tag_len = si32(fh)
        tag_payload = fh.read(tag_len)
        if b"Este programa vuelve a emi" in tag_payload:
            print(ident + "ASSSSSSSSSSSSSSSSSSDT")
        tag_name, tag_func = TAGS[tag_type]
        if tag_func is None:
            if len(tag_payload) > 30:
                result = repr(tag_payload[:30]) + " (...)"
            else:
                result = repr(tag_payload)
            print(ident + "%s: %s" % (tag_name, result))
        else:
            print(ident + "%s:" % (tag_name,))
            tag_func(tag_payload, ident + "    ")


def handle_definesprite(data, ident):
    """Handle DefineSprite."""
    src = io.BytesIO(data)
    character_id = ui16(src)
    print(ident + "CharacterID:", character_id)
    print(ident + "FrameCount:", ui16(src))
    print(ident + "Tags:")
    process_tags(src, ident=ident + "    ")


def handle_actionconstantpool(data, ident):
    """Handle ActionConstantPool."""
    src = io.BytesIO(data)
    count = ui16(src)
    print(ident + "Count:", count)
    for _ in range(count):
        print(ident + string(src))


ACTIONS = {
    0x04: ('ActionNextFrame', None),
    0x05: ('ActionPrevFrame', None),
    0x06: ('ActionPlay', None),
    0x07: ('ActionStop', None),
    0x08: ('ActionToggleQualty', None),
    0x09: ('ActionStopSounds', None),
    0x0A: ('ActionAdd', None),
    0x0B: ('ActionSubtract', None),
    0x0C: ('ActionMultiply', None),
    0x0D: ('ActionDivide', None),
    0x0E: ('ActionEquals', None),
    0x0F: ('ActionLess', None),
    0x10: ('ActionAnd', None),
    0x11: ('ActionOr', None),
    0x12: ('ActionNot', None),
    0x13: ('ActionStringEquals', None),
    0x14: ('ActionStringLength', None),
    0x15: ('ActionStringExtract', None),
    0x17: ('ActionPop', None),
    0x18: ('ActionToInteger', None),
    0x1C: ('ActionGetVariable', None),
    0x1D: ('ActionSetVariable', None),
    0x20: ('ActionSetTarget2', None),
    0x21: ('ActionStringAdd', None),
    0x22: ('ActionGetProperty', None),
    0x23: ('ActionSetProperty', None),
    0x24: ('ActionCloneSprite', None),
    0x25: ('ActionRemoveSprite', None),
    0x26: ('ActionTrace', None),
    0x27: ('ActionStartDrag', None),
    0x28: ('ActionEndDrag', None),
    0x29: ('ActionStringLess', None),
    0x2A: ('ActionThrow', None),
    0x2B: ('ActionCastOp', None),
    0x2C: ('ActionImplementsOp', None),
    0x30: ('ActionRandomNumber', None),
    0x31: ('ActionMBStringLength', None),
    0x32: ('ActionCharToAscii', None),
    0x33: ('ActionAsciiToChar', None),
    0x34: ('ActionGetTime', None),
    0x35: ('ActionMBStringExtract', None),
    0x36: ('ActionMBCharToAscii', None),
    0x37: ('ActionMBAsciiToChar', None),
    0x3A: ('ActionDelete', None),
    0x3B: ('ActionDelete2', None),
    0x3C: ('ActionDefineLocal', None),
    0x3D: ('ActionCallFunction', None),
    0x3E: ('ActionReturn', None),
    0x3F: ('ActionModulo', None),
    0x40: ('ActionNewObject', None),
    0x41: ('ActionDefineLocal2', None),
    0x42: ('ActionInitArray', None),
    0x43: ('ActionInitObject', None),
    0x44: ('ActionTypeOf', None),
    0x45: ('ActionTargetPath', None),
    0x46: ('ActionEnumerate', None),
    0x47: ('ActionAdd2', None),
    0x48: ('ActionLess2', None),
    0x49: ('ActionEquals2', None),
    0x4A: ('ActionToNumber', None),
    0x4B: ('ActionToString', None),
    0x4C: ('ActionPushDuplicate', None),
    0x4D: ('ActionStackSwap', None),
    0x4E: ('ActionGetMember', None),
    0x4F: ('ActionSetMember', None),
    0x50: ('ActionIncrement', None),
    0x51: ('ActionDecrement', None),
    0x52: ('ActionCallMethod', None),
    0x53: ('ActionNewMethod', None),
    0x54: ('ActionInstanceOf', None),
    0x55: ('ActionEnumerate2', None),
    0x60: ('ActionBitAnd', None),
    0x61: ('ActionBitOr', None),
    0x62: ('ActionBitXor', None),
    0x63: ('ActionBitLShift', None),
    0x64: ('ActionBitRShift', None),
    0x65: ('ActionBitURShift', None),
    0x66: ('ActionStrictEquals', None),
    0x67: ('ActionGreater', None),
    0x68: ('ActionStringGreater', None),
    0x69: ('ActionExtends', None),
    0x81: ('ActionGotoFrame', None),
    0x83: ('ActionGetURL', None),
    0x87: ('ActionStoreRegister', None),
    0x88: ('ActionConstantPool', handle_actionconstantpool),
    0x8A: ('ActionWaitForFrame', None),
    0x8B: ('ActionSetTarget', None),
    0x8C: ('ActionGoToLabel', None),
    0x8D: ('ActionWaitForFrame2', None),
    0x8E: ('ActionDefineFunction2', None),
    0x8F: ('ActionTry', None),
    0x94: ('ActionWith', None),
    0x96: ('ActionPush', None),
    0x99: ('ActionJump', None),
    0x9A: ('ActionGetURL2', None),
    0x9B: ('ActionDefineFunction', None),
    0x9D: ('ActionIf', None),
    0x9E: ('ActionCall', None),
    0x9F: ('ActionGotoFrame2', None),
}

def handle_doaction(data, ident):
    """Handle DoAction."""
    src = io.BytesIO(data)
    while True:
        action_code = ui8(src)
        if action_code == 0:
            break
        try:
            action_name, action_func = ACTIONS[action_code]
        except KeyError:
            action_name, action_func = "--(unknown)--", None
        if action_code > 128:
            length = ui16(src)
            payload = src.read(length)
            if action_func is None:
                print("%s%s (%d) %r" % (ident, action_name,
                                        action_code, payload))
            else:
                print("%s%s (%d)" % (ident, action_name, action_code))
                action_func(payload, ident + "    ")
        else:
            print("%s%s (%d)" % (ident, action_name, action_code))


# reference from tag type to its name and processing function (None: no func)
TAGS = {
    0: ("End", None),
    1: ("ShowFrame", None),
    2: ("DefineShape", None),
    4: ("PlaceObject", None),
    5: ("RemoveObject", None),
    6: ("DefineBits", handle_definebits),
    7: ("DefineButton", None),
    8: ("JPEGTables", None),
    9: ("SetBackgroundColor", None),
    10: ("DefineFont", None),
    11: ("DefineText", None),
    12: ("DoAction", handle_doaction),
    13: ("DefineFontInfo", None),
    14: ("DefineSound", None),
    15: ("StartSound", None),
    17: ("DefineButtonSound", None),
    18: ("SoundStreamHead", None),
    19: ("SoundStreamBlock", None),
    20: ("DefineBitsLossless", None),
    21: ("DefineBitsJPEG2", None),
    22: ("DefineShape2", None),
    23: ("DefineButtonCxform", None),
    24: ("Protect", None),
    26: ("PlaceObject2", None),
    28: ("RemoveObject2", None),
    32: ("DefineShape3", None),
    33: ("DefineText2", None),
    34: ("DefineButton2", None),
    35: ("DefineBitsJPEG3", None),
    36: ("DefineBitsLossless2", None),
    37: ("DefineEditText", handle_defineedittext),
    39: ("DefineSprite", handle_definesprite),
    43: ("FrameLabel", None),
    45: ("SoundStreamHead2", None),
    46: ("DefineMorphShape", None),
    48: ("DefineFont2", None),
    56: ("ExportAssets", None),
    57: ("ImportAssets", None),
    58: ("EnableDebugger", None),
    59: ("DoInitAction", None),
    60: ("DefineVideoStream", None),
    61: ("VideoFrame", None),
    62: ("DefineFontInfo2", None),
    64: ("EnableDebugger2", None),
    65: ("ScriptLimits", None),
    66: ("SetTabIndex", None),
    69: ("FileAttributes", None),
    70: ("PlaceObject3", None),
    71: ("ImportAssets2", None),
    73: ("DefineFontAlignZones", None),
    74: ("CSMTextSettings", None),
    75: ("DefineFont3", None),
    76: ("SymbolClass", None),
    77: ("Metadata", None),
    78: ("DefineScalingGrid", None),
    82: ("DoABC", None),
    83: ("DefineShape4", None),
    84: ("DefineMorphShape2", None),
    86: ("DefineSceneAndFrameLabelData", None),
    87: ("DefineBinaryData", None),
    88: ("DefineFontName", None),
    89: ("StartSound2", None),
    90: ("DefineBitsJPEG4", None),
    91: ("DefineFont4", None),
}



def test():
    """Test."""
    src = io.BytesIO(b'\x08')
    assert ui8(src) == 0x08

    src = io.BytesIO(b'\x98\x19\x02\x00')
    assert ui32(src) == 137624

    src = io.BytesIO(b'\x1b\xae\x80')
    assert rect(src) == (3, 5, 3, 5)
    src = io.BytesIO(b'\x70\x00\x0a\x8c\x00\x00\xda\xc0')
    assert rect(src) == (0, 5400, 0, 7000)


def main(fname):
    """Main entry point."""
    fh = open(fname, 'rb')

    # get the first part of the header
    signature = chr(ui8(fh)) + chr(ui8(fh)) + chr(ui8(fh))
    print("(header) Signature:", signature)
    print("(header) Version:", ui8(fh))
    flength = int(ui32(fh))
    print("(header) File length:", flength)

    # deal with compressed content
    if signature[0] == 'C':
        uncompressed = zlib.decompress(fh.read())
        if len(uncompressed) + 8 != flength:
            raise ValueError("Problems dealing with compressed content")
        fh = io.BytesIO(uncompressed)

    # second part of the header
    print("(header) Frame size:", rect(fh))
    print("(header) Frame rate:", ui16(fh))
    print("(header) Frame count:", ui16(fh))

    # tags
    process_tags(fh)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: swfparser.py {--test|file.swf}")
        exit()

    if sys.argv[1] == '--test':
        test()
    else:
        main(sys.argv[1])
