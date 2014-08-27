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

"""Parse a SWF file and expose all its internals.

This follows the SWF FILE FORMAT SPECIFICATION VERSION 19 which is not
included in this project for your easier finding because Adobe forbids
the spec distribution.

The attributes names are CamelCase to match as close as possible the
spec.

Note: not all the spec is covered (work in progress!), there's a flag
in the SWFParser to change the behaviour when an still-not-done object
is found.
"""

import collections
import io
import zlib

from .helpers import (
    BitConsumer,
    ReadQuantityController,
    unpack_si16,
    unpack_ui16,
    unpack_ui32,
    unpack_ui8,
    unpack_fixed8,
    unpack_fixed16,
    unpack_float16,
    unpack_float,
    unpack_double,
)

VERSION = "0.9.3"

# name of each tag (as a dict, not a list, for easier human consumption)
TAG_NAMES = {
    0: "End",
    1: "ShowFrame",
    2: "DefineShape",
    4: "PlaceObject",
    5: "RemoveObject",
    6: "DefineBits",
    7: "DefineButton",
    8: "JPEGTables",
    9: "SetBackgroundColor",
    10: "DefineFont",
    11: "DefineText",
    12: "DoAction",
    13: "DefineFontInfo",
    14: "DefineSound",
    15: "StartSound",
    17: "DefineButtonSound",
    18: "SoundStreamHead",
    19: "SoundStreamBlock",
    20: "DefineBitsLossless",
    21: "DefineBitsJPEG2",
    22: "DefineShape2",
    23: "DefineButtonCxform",
    24: "Protect",
    26: "PlaceObject2",
    28: "RemoveObject2",
    32: "DefineShape3",
    33: "DefineText2",
    34: "DefineButton2",
    35: "DefineBitsJPEG3",
    36: "DefineBitsLossless2",
    37: "DefineEditText",
    39: "DefineSprite",
    43: "FrameLabel",
    45: "SoundStreamHead2",
    46: "DefineMorphShape",
    48: "DefineFont2",
    56: "ExportAssets",
    57: "ImportAssets",
    58: "EnableDebugger",
    59: "DoInitAction",
    60: "DefineVideoStream",
    61: "VideoFrame",
    62: "DefineFontInfo2",
    64: "EnableDebugger2",
    65: "ScriptLimits",
    66: "SetTabIndex",
    69: "FileAttributes",
    70: "PlaceObject3",
    71: "ImportAssets2",
    73: "DefineFontAlignZones",
    74: "CSMTextSettings",
    75: "DefineFont3",
    76: "SymbolClass",
    77: "Metadata",
    78: "DefineScalingGrid",
    82: "DoABC",
    83: "DefineShape4",
    84: "DefineMorphShape2",
    86: "DefineSceneAndFrameLabelData",
    87: "DefineBinaryData",
    88: "DefineFontName",
    89: "StartSound2",
    90: "DefineBitsJPEG4",
    91: "DefineFont4",
}

LANGCODES = {
    1: "Latin",
    2: "Japanese",
    3: "Korean",
    4: "Simplified Chinese",
    5: "Traditional Chinese",
}

ACTION_NAMES = {
    0x04: 'ActionNextFrame',
    0x05: 'ActionPrevFrame',
    0x06: 'ActionPlay',
    0x07: 'ActionStop',
    0x08: 'ActionToggleQualty',
    0x09: 'ActionStopSounds',
    0x0A: 'ActionAdd',
    0x0B: 'ActionSubtract',
    0x0C: 'ActionMultiply',
    0x0D: 'ActionDivide',
    0x0E: 'ActionEquals',
    0x0F: 'ActionLess',
    0x10: 'ActionAnd',
    0x11: 'ActionOr',
    0x12: 'ActionNot',
    0x13: 'ActionStringEquals',
    0x14: 'ActionStringLength',
    0x15: 'ActionStringExtract',
    0x17: 'ActionPop',
    0x18: 'ActionToInteger',
    0x1C: 'ActionGetVariable',
    0x1D: 'ActionSetVariable',
    0x20: 'ActionSetTarget2',
    0x21: 'ActionStringAdd',
    0x22: 'ActionGetProperty',
    0x23: 'ActionSetProperty',
    0x24: 'ActionCloneSprite',
    0x25: 'ActionRemoveSprite',
    0x26: 'ActionTrace',
    0x27: 'ActionStartDrag',
    0x28: 'ActionEndDrag',
    0x29: 'ActionStringLess',
    0x2A: 'ActionThrow',
    0x2B: 'ActionCastOp',
    0x2C: 'ActionImplementsOp',
    0x30: 'ActionRandomNumber',
    0x31: 'ActionMBStringLength',
    0x32: 'ActionCharToAscii',
    0x33: 'ActionAsciiToChar',
    0x34: 'ActionGetTime',
    0x35: 'ActionMBStringExtract',
    0x36: 'ActionMBCharToAscii',
    0x37: 'ActionMBAsciiToChar',
    0x3A: 'ActionDelete',
    0x3B: 'ActionDelete2',
    0x3C: 'ActionDefineLocal',
    0x3D: 'ActionCallFunction',
    0x3E: 'ActionReturn',
    0x3F: 'ActionModulo',
    0x40: 'ActionNewObject',
    0x41: 'ActionDefineLocal2',
    0x42: 'ActionInitArray',
    0x43: 'ActionInitObject',
    0x44: 'ActionTypeOf',
    0x45: 'ActionTargetPath',
    0x46: 'ActionEnumerate',
    0x47: 'ActionAdd2',
    0x48: 'ActionLess2',
    0x49: 'ActionEquals2',
    0x4A: 'ActionToNumber',
    0x4B: 'ActionToString',
    0x4C: 'ActionPushDuplicate',
    0x4D: 'ActionStackSwap',
    0x4E: 'ActionGetMember',
    0x4F: 'ActionSetMember',
    0x50: 'ActionIncrement',
    0x51: 'ActionDecrement',
    0x52: 'ActionCallMethod',
    0x53: 'ActionNewMethod',
    0x54: 'ActionInstanceOf',
    0x55: 'ActionEnumerate2',
    0x60: 'ActionBitAnd',
    0x61: 'ActionBitOr',
    0x62: 'ActionBitXor',
    0x63: 'ActionBitLShift',
    0x64: 'ActionBitRShift',
    0x65: 'ActionBitURShift',
    0x66: 'ActionStrictEquals',
    0x67: 'ActionGreater',
    0x68: 'ActionStringGreater',
    0x69: 'ActionExtends',
    0x81: 'ActionGotoFrame',
    0x83: 'ActionGetURL',
    0x87: 'ActionStoreRegister',
    0x88: 'ActionConstantPool',
    0x8A: 'ActionWaitForFrame',
    0x8B: 'ActionSetTarget',
    0x8C: 'ActionGoToLabel',
    0x8D: 'ActionWaitForFrame2',
    0x8E: 'ActionDefineFunction2',
    0x8F: 'ActionTry',
    0x94: 'ActionWith',
    0x96: 'ActionPush',
    0x99: 'ActionJump',
    0x9A: 'ActionGetURL2',
    0x9B: 'ActionDefineFunction',
    0x9D: 'ActionIf',
    0x9E: 'ActionCall',
    0x9F: 'ActionGotoFrame2',
}


def _str(obj):
    """Show nicely the generic object received."""
    values = []
    for name in obj._attribs:
        val = getattr(obj, name)
        if isinstance(val, str):
            val = repr(val)
        val = str(val) if len(str(val)) < 10 else "(...)"
        values.append((name, val))
    values = ", ".join("{}={}".format(k, v) for k, v in values)
    return "{}({})".format(obj.__class__.__name__, values)


def _repr(obj):
    """Show the received object as precise as possible."""
    vals = ", ".join("{}={!r}".format(
        name, getattr(obj, name)) for name in obj._attribs)
    if vals:
        t = "{}(name={}, {})".format(obj.__class__.__name__, obj.name, vals)
    else:
        t = "{}(name={})".format(obj.__class__.__name__, obj.name)
    return t


class SWFObject:
    """A super class for all the objects created here."""

    def __init__(self):
        self._attribs = []

    def __setattr__(self, name, value):
        if name != "_attribs":
            if name not in self._attribs:
                self._attribs.append(name)
        super(SWFObject, self).__setattr__(name, value)


def _make_object(name):
    """Create a generic object for the tags."""
    klass = type(name, (SWFObject,),
                 {'__str__': _str, '__repr__': _repr, 'name': name})
    return klass()


class SWFParser:
    """Read (at a byte or bit level) the SWF structure from a fileobject.

    When the parser finds a structure that still can't process (because more
    programming is needed), will just return an UnknownObject object with
    the unparsed bytes, or will raise an exception if you set
    the unknown_alert flag::

        SWFParser.unknown_alert = True
    """

    unknown_alert = False

    def __init__(self, src):
        self._src = src
        self._version = None
        self._last_defined_glyphs_quantity = None
        self.header = self._get_header()
        self.tags = self._process_tags()

    def _get_header(self):
        """Parse the SWF header."""
        fh = self._src
        obj = _make_object("Header")

        # first part of the header
        obj.Signature = sign = "".join(chr(unpack_ui8(fh)) for _ in range(3))
        obj.Version = self._version = unpack_ui8(fh)
        obj.FileLength = file_length = unpack_ui32(fh)

        # deal with compressed content
        if sign[0] == 'C':
            uncompressed = zlib.decompress(fh.read())
            if len(uncompressed) + 8 != file_length:
                raise ValueError("Problems dealing with compressed content")
            fh = self._src = io.BytesIO(uncompressed)

        # second part of the header
        obj.FrameSize = self._get_struct_rect()
        obj.FrameRate = unpack_ui16(fh)
        obj.FrameCount = unpack_ui16(fh)
        return obj

    def _process_tags(self):
        """Get a sequence of tags."""
        tags = []

        while True:
            tag_bf = unpack_ui16(self._src)
            tag_type = tag_bf >> 6   # upper 10 bits
            if tag_type == 0:
                # the end
                break
            tag_len = tag_bf & 0x3f  # last 6 bits
            if tag_len == 0x3f:
                # the length is the next four bytes!
                tag_len = unpack_ui32(self._src)

            try:
                tag_name = TAG_NAMES[tag_type]
            except KeyError:
                # malformed SWF, create and unknown object with malformed tag
                tag_payload = self._src.read(tag_len)
                _dict = {
                    '__str__': _repr,
                    '__repr__': _repr,
                    'name': 'UnspecifiedObject(tag={!r})'.format(tag_type),
                }
                tag = type("UnknownObject", (SWFObject,), _dict)()
                tag.raw_payload = tag_payload
                tags.append(tag)
                continue

            try:
                tag_meth = getattr(self, "_handle_tag_" + tag_name.lower())
            except AttributeError:
                if self.unknown_alert:
                    raise ValueError("Unknown tag: " + repr(tag_name))

                tag_payload = self._src.read(tag_len)
                _dict = {'__str__': _repr, '__repr__': _repr, 'name': tag_name}
                tag = type("UnknownObject", (SWFObject,), _dict)()
                tag.raw_payload = tag_payload
                tags.append(tag)
                continue

            # we know the tag type, and have the handler, let's process it
            prev_pos = self._src.tell()
            self._src.guard = tag_len
            try:
                with ReadQuantityController(self._src, tag_len):
                    tag = tag_meth()
                assert tag is not None, tag_name
            except ValueError:
                # an attempt to read too much happened; create a failing
                # object with the raw payload
                self._src.guard = None
                self._src.seek(prev_pos)
                tag_payload = self._src.read(tag_len)
                _dict = {'__str__': _repr, '__repr__': _repr, 'name': tag_name}
                tag = type("FailingObject", (SWFObject,), _dict)()
                tag.raw_payload = tag_payload
            tags.append(tag)
        return tags

    def _handle_tag_definebits(self):
        """Handle the DefineBits tag."""
        obj = _make_object("DefineBits")
        obj.CharacterID = unpack_ui16(self._src)
        assert self._src.read(2) == b'\xFF\xD8'  # SOI marker
        eoimark1 = eoimark2 = None
        allbytes = []
        while not (eoimark1 == b'\xFF' and eoimark2 == b'\xD9'):
            newbyte = self._src.read(1)
            allbytes.append(newbyte)
            eoimark1 = eoimark2
            eoimark2 = newbyte

        # concatenate everything, removing the end mark
        obj.JPEGData = b"".join(allbytes)
        return obj

    def _handle_tag_definebitsjpeg2(self):
        """Handle the DefineBitsJPEG2 tag."""
        obj = _make_object("DefineBitsJPEG2")
        obj.CharacterID = unpack_ui16(self._src)
        assert self._src.read(2) == b'\xFF\xD8'  # SOI marker
        eoimark1 = eoimark2 = None
        allbytes = []
        while not (eoimark1 == b'\xFF' and eoimark2 == b'\xD9'):
            newbyte = self._src.read(1)
            allbytes.append(newbyte)
            eoimark1 = eoimark2
            eoimark2 = newbyte

        # concatenate everything, removing the end mark
        obj.ImageData = b"".join(allbytes)
        return obj

    def _generic_definetext_parser(self, obj, rgb_struct):
        """Generic parser for the DefineTextN tags."""
        obj.CharacterID = unpack_ui16(self._src)
        obj.TextBounds = self._get_struct_rect()
        obj.TextMatrix = self._get_struct_matrix()
        obj.GlyphBits = glyph_bits = unpack_ui8(self._src)
        obj.AdvanceBits = advance_bits = unpack_ui8(self._src)

        # textrecords
        obj.TextRecords = records = []
        while True:
            endofrecords_flag = unpack_ui8(self._src)
            if endofrecords_flag == 0:
                # all done
                obj.EndOfRecordsFlag = 0
                break

            # we have a TEXTRECORD, let's go back the 8 bits and set the obj
            self._src.seek(-1, io.SEEK_CUR)
            record = _make_object("TextRecord")
            records.append(record)

            bc = BitConsumer(self._src)
            record.TextRecordType = bc.u_get(1)
            record.StyleFlagsReserved = bc.u_get(3)
            record.StyleFlagsHasFont = bc.u_get(1)
            record.StyleFlagsHasColor = bc.u_get(1)
            record.StyleFlagsHasYOffset = bc.u_get(1)
            record.StyleFlagsHasXOffset = bc.u_get(1)

            if record.StyleFlagsHasFont:
                record.FontID = unpack_ui16(self._src)
            if record.StyleFlagsHasColor:
                record.TextColor = rgb_struct()
            if record.StyleFlagsHasXOffset:
                record.XOffset = unpack_si16(self._src)
            if record.StyleFlagsHasYOffset:
                record.YOffset = unpack_si16(self._src)
            if record.StyleFlagsHasFont:
                record.TextHeight = unpack_ui16(self._src)

            record.GlyphCount = unpack_ui8(self._src)
            bc = BitConsumer(self._src)
            record.GlyphEntries = glyphs = []
            for _ in range(record.GlyphCount):
                glyph = _make_object("GlyphEntry")
                glyphs.append(glyph)
                glyph.GlyphIndex = bc.u_get(glyph_bits)
                glyph.GlyphAdvance = bc.u_get(advance_bits)

    def _handle_tag_definetext(self):
        """Handle the DefineText tag."""
        obj = _make_object("DefineText")
        self._generic_definetext_parser(obj, self._get_struct_rgb)
        return obj

    def _handle_tag_definetext2(self):
        """Handle the DefineText2 tag."""
        obj = _make_object("DefineText2")
        self._generic_definetext_parser(obj, self._get_struct_rgba)
        return obj

    def _handle_tag_defineedittext(self):
        """Handle the DefineEditText tag."""
        obj = _make_object("DefineEditText")
        obj.CharacterID = unpack_ui16(self._src)
        obj.Bounds = self._get_struct_rect()

        bc = BitConsumer(self._src)
        obj.HasText = bc.u_get(1)
        obj.WordWrap = bc.u_get(1)
        obj.Multiline = bc.u_get(1)
        obj.Password = bc.u_get(1)
        obj.ReadOnly = bc.u_get(1)
        obj.HasTextColor = bc.u_get(1)
        obj.HasMaxLength = bc.u_get(1)
        obj.HasFont = bc.u_get(1)
        obj.HasFontClass = bc.u_get(1)
        obj.AutoSize = bc.u_get(1)
        obj.HasLayout = bc.u_get(1)
        obj.NoSelect = bc.u_get(1)
        obj.Border = bc.u_get(1)
        obj.WasStatic = bc.u_get(1)
        obj.HTML = bc.u_get(1)
        obj.UseOutlines = bc.u_get(1)

        if obj.HasFont:
            obj.FontID = unpack_ui16(self._src)
        if obj.HasFontClass:
            obj.FontClass = self._get_struct_string()
        if obj.HasFont:
            obj.FontHeight = unpack_ui16(self._src)
        if obj.HasTextColor:
            obj.TextColor = self._get_struct_rgba()
        if obj.HasMaxLength:
            obj.MaxLength = unpack_ui16(self._src)
        if obj.HasLayout:
            obj.Align = unpack_ui8(self._src)
            obj.LeftMargin = unpack_ui16(self._src)
            obj.RightMargin = unpack_ui16(self._src)
            obj.Indent = unpack_ui16(self._src)
            obj.Leading = unpack_ui16(self._src)

        obj.VariableName = self._get_struct_string()
        if obj.HasText:
            obj.InitialText = self._get_struct_string()
        return obj

    def _generic_placeobject_parser(self, obj, version):
        """A generic parser for several PlaceObjectX."""
        bc = BitConsumer(self._src)
        obj.PlaceFlagHasClipActions = bc.u_get(1)
        obj.PlaceFlagHasClipDepth = bc.u_get(1)
        obj.PlaceFlagHasName = bc.u_get(1)
        obj.PlaceFlagHasRatio = bc.u_get(1)
        obj.PlaceFlagHasColorTransform = bc.u_get(1)
        obj.PlaceFlagHasMatrix = bc.u_get(1)
        obj.PlaceFlagHasCharacter = bc.u_get(1)
        obj.PlaceFlagMove = bc.u_get(1)

        if version == 3:
            obj.Reserved = bc.u_get(1)
            obj.PlaceFlagOpaqueBackground = bc.u_get(1)
            obj.PlaceFlagHasVisible = bc.u_get(1)
            obj.PlaceFlagHasImage = bc.u_get(1)
            obj.PlaceFlagHasClassName = bc.u_get(1)
            obj.PlaceFlagHasCacheAsBitmap = bc.u_get(1)
            obj.PlaceFlagHasBlendMode = bc.u_get(1)
            obj.PlaceFlagHasFilterList = bc.u_get(1)

        obj.Depth = unpack_ui16(self._src)

        if version == 3:
            if obj.PlaceFlagHasClassName or (
                    obj.PlaceFlagHasImage and obj.PlaceFlagHasCharacter):
                obj.ClassName = self._get_struct_string()

        if obj.PlaceFlagHasCharacter:
            obj.CharacterId = unpack_ui16(self._src)
        if obj.PlaceFlagHasMatrix:
            obj.Matrix = self._get_struct_matrix()
        if obj.PlaceFlagHasColorTransform:
            obj.ColorTransform = self._get_struct_cxformwithalpha()
        if obj.PlaceFlagHasRatio:
            obj.Ratio = unpack_ui16(self._src)
        if obj.PlaceFlagHasName:
            obj.Name = self._get_struct_string()
        if obj.PlaceFlagHasClipDepth:
            obj.ClipDepth = unpack_ui16(self._src)

        if version == 3:
            if obj.PlaceFlagHasFilterList:
                obj.SurfaceFilterList = self._get_struct_filterlist()
            if obj.PlaceFlagHasBlendMode:
                obj.BlendMode = unpack_ui8(self._src)
            if obj.PlaceFlagHasCacheAsBitmap:
                obj.BitmapCache = unpack_ui8(self._src)
            if obj.PlaceFlagHasVisible:
                obj.Visible = unpack_ui8(self._src)
                obj.BackgroundColor = self._get_struct_rgba()

        if obj.PlaceFlagHasClipActions:
            obj.ClipActions = self._get_struct_clipactions()

    def _handle_tag_placeobject2(self):
        """Handle the PlaceObject2 tag."""
        obj = _make_object("PlaceObject2")
        self._generic_placeobject_parser(obj, 2)
        return obj

    def _handle_tag_placeobject3(self):
        """Handle the PlaceObject3 tag."""
        obj = _make_object("PlaceObject3")
        self._generic_placeobject_parser(obj, 3)
        return obj

    def _handle_tag_definesprite(self):
        """Handle the DefineSprite tag."""
        obj = _make_object("DefineSprite")
        obj.CharacterID = unpack_ui16(self._src)
        obj.FrameCount = unpack_ui16(self._src)
        tags = self._process_tags()
        obj.ControlTags = tags
        return obj

    def _generic_action_parser(self):
        """Generic parser for Actions."""
        actions = []
        while True:
            action_code = unpack_ui8(self._src)
            if action_code == 0:
                break

            action_name = ACTION_NAMES[action_code]
            if action_code > 128:
                # have a payload!
                action_len = unpack_ui16(self._src)
                try:
                    action_meth = getattr(
                        self, "_handle_" + action_name.lower())
                except AttributeError:
                    if self.unknown_alert:
                        raise ValueError(
                            "Unknown action: " + repr(action_name))

                    action_payload = self._src.read(action_len)
                    _dict = {'__str__': _repr, '__repr__': _repr,
                             'name': action_name}
                    action = type("UnknownAction", (SWFObject,), _dict)()
                    action.raw_payload = action_payload
                    actions.append(action)
                else:
                    prev_pos = self._src.tell()
                    for action in action_meth(action_len):
                        assert action is not None, action_name
                        actions.append(action)

                    quant_read = self._src.tell() - prev_pos
                    if quant_read != action_len:
                        raise RuntimeError(
                            "Bad bytes consumption by action {!r} handler "
                            "(did {}, should {})".format(
                                action_name, quant_read, action_len))
            else:
                action = _make_object(action_name)
                actions.append(action)
        return actions

    def _handle_tag_doaction(self):
        """Handle the DoAction tag."""
        obj = _make_object("DoAction")
        obj.Actions = self._generic_action_parser()
        return obj

    def _handle_tag_fileattributes(self):
        """Handle the FileAttributes tag."""
        obj = _make_object("FileAttributes")
        bc = BitConsumer(self._src)

        bc.u_get(1)  # reserved
        obj.UseDirectBlit = bc.u_get(1)
        obj.UseGPU = bc.u_get(1)
        obj.HasMetadata = bc.u_get(1)
        obj.ActionScript3 = bc.u_get(1)
        bc.u_get(2)  # reserved
        obj.UseNetwork = bc.u_get(1)
        bc.u_get(24)  # reserved
        return obj

    def _handle_tag_metadata(self):
        """Handle the Metadata tag."""
        obj = _make_object("Metadata")
        obj.Metadata = self._get_struct_string()
        return obj

    def _handle_tag_setbackgroundcolor(self):
        """Handle the SetBackgroundColor tag."""
        obj = _make_object("SetBackgroundColor")
        obj.BackgroundColor = self._get_struct_rgb()
        return obj

    def _handle_tag_definesceneandframelabeldata(self):
        """Handle the DefineSceneAndFrameLabelData tag."""
        obj = _make_object("DefineSceneAndFrameLabelData")
        obj.SceneCount = self._get_struct_encodedu32()
        for i in range(1, obj.SceneCount + 1):
            setattr(obj, 'Offset{}'.format(i), self._get_struct_encodedu32())
            setattr(obj, 'Name{}'.format(i), self._get_struct_string())
        obj.FrameLabelCount = self._get_struct_encodedu32()
        for i in range(1, obj.FrameLabelCount + 1):
            setattr(obj, 'FrameNum{}'.format(i), self._get_struct_encodedu32())
            setattr(obj, 'FrameLabel{}'.format(i), self._get_struct_string())
        return obj

    def _handle_tag_defineshape4(self):
        """Handle the DefineShape4 tag."""
        obj = _make_object("DefineShape4")
        obj.ShapeId = unpack_ui16(self._src)
        obj.ShapeBounds = self._get_struct_rect()
        obj.EdgeBounds = self._get_struct_rect()

        bc = BitConsumer(self._src)
        bc.u_get(5)  # reserved
        obj.UsesFillWindingRule = bc.u_get(1)
        obj.UsesNonScalingStrokes = bc.u_get(1)
        obj.UsesScalingStrokes = bc.u_get(1)
        obj.Shapes = self._get_struct_shapewithstyle(4)
        return obj

    def _handle_tag_definemorphshape2(self):
        """Handle the DefineMorphShape2 tag."""
        obj = _make_object("DefineMorphShape2")
        obj.CharacterId = unpack_ui16(self._src)
        obj.StartBounds = self._get_struct_rect()
        obj.EndBounds = self._get_struct_rect()
        obj.StartEdgeBounds = self._get_struct_rect()
        obj.EndEdgeBounds = self._get_struct_rect()

        bc = BitConsumer(self._src)
        bc.u_get(6)  # reserved
        obj.UsesNonScalingStrokes = bc.u_get(1)
        obj.UsesScalingStrokes = bc.u_get(1)

        obj.Offset = unpack_ui32(self._src)

        # FIXME: this tag needs more work; I'm skipping some attributes here
        self._src.read(obj.Offset)

        obj.EndEdges = self._get_struct_shape()
        return obj

    def _handle_tag_showframe(self):
        """Handle the ShowFrame tag."""
        return _make_object("ShowFrame")

    def _handle_tag_removeobject(self):
        """Handle the RemoveObject tag."""
        obj = _make_object("RemoveObject")
        obj.CharacterId = unpack_ui16(self._src)
        obj.Depth = unpack_ui16(self._src)
        return obj

    def _handle_tag_removeobject2(self):
        """Handle the RemoveObject2 tag."""
        obj = _make_object("RemoveObject2")
        obj.Depth = unpack_ui16(self._src)
        return obj

    def _handle_tag_defineshape(self):
        """Handle the DefineShape tag."""
        obj = _make_object("DefineShape")
        obj.ShapeId = unpack_ui16(self._src)
        obj.ShapeBounds = self._get_struct_rect()
        obj.Shapes = self._get_struct_shapewithstyle(1)
        return obj

    def _handle_tag_defineshape2(self):
        """Handle the DefineShape2 tag."""
        obj = _make_object("DefineShape2")
        obj.ShapeId = unpack_ui16(self._src)
        obj.ShapeBounds = self._get_struct_rect()
        obj.Shapes = self._get_struct_shapewithstyle(2)
        return obj

    def _handle_tag_defineshape3(self):
        """Handle the DefineShape3 tag."""
        obj = _make_object("DefineShape3")
        obj.ShapeId = unpack_ui16(self._src)
        obj.ShapeBounds = self._get_struct_rect()
        obj.Shapes = self._get_struct_shapewithstyle(3)
        return obj

    def _generic_definefont_parser(self, obj):
        """A generic parser for several DefineFontX."""
        obj.FontID = unpack_ui16(self._src)

        bc = BitConsumer(self._src)
        obj.FontFlagsHasLayout = bc.u_get(1)
        obj.FontFlagsShiftJIS = bc.u_get(1)
        obj.FontFlagsSmallText = bc.u_get(1)
        obj.FontFlagsANSI = bc.u_get(1)
        obj.FontFlagsWideOffsets = bc.u_get(1)
        obj.FontFlagsWideCodes = bc.u_get(1)
        obj.FontFlagsItalic = bc.u_get(1)
        obj.FontFlagsBold = bc.u_get(1)

        obj.LanguageCode = self._get_struct_langcode()
        obj.FontNameLen = unpack_ui8(self._src)
        obj.FontName = "".join(chr(unpack_ui8(self._src))
                               for i in range(obj.FontNameLen))
        if obj.FontName[-1] == '\x00':  # most probably ends in null, clean it
            obj.FontName = obj.FontName[:-1]

        obj.NumGlyphs = num_glyphs = unpack_ui16(self._src)
        self._last_defined_glyphs_quantity = num_glyphs
        getter_wide = unpack_ui32 if obj.FontFlagsWideOffsets else unpack_ui16
        obj.OffsetTable = [getter_wide(self._src) for _ in range(num_glyphs)]
        obj.CodeTableOffset = getter_wide(self._src)
        obj.GlyphShapeTable = [self._get_struct_shape()
                               for _ in range(num_glyphs)]
        obj.CodeTable = [unpack_ui16(self._src) for _ in range(num_glyphs)]

        if obj.FontFlagsHasLayout:
            obj.FontAscent = unpack_ui16(self._src)
            obj.FontDecent = unpack_ui16(self._src)
            obj.FontLeading = unpack_ui16(self._src)
            obj.FontAdvanceTable = [unpack_si16(self._src)
                                    for _ in range(num_glyphs)]
            obj.FontBoundsTable = [self._get_struct_rect()
                                   for _ in range(num_glyphs)]
            obj.KerningCount = unpack_ui16(self._src)
            obj.FontKerningTable = [
                self._get_struct_kerningrecord(obj.FontFlagsWideCodes)
                for _ in range(obj.KerningCount)]

    def _handle_tag_definefont2(self):
        """Handle the DefineFont2 tag."""
        obj = _make_object("DefineFont2")
        self._generic_definefont_parser(obj)
        return obj

    def _handle_tag_definefont3(self):
        """Handle the DefineFont3 tag."""
        obj = _make_object("DefineFont3")
        self._generic_definefont_parser(obj)
        return obj

    def _handle_tag_definebutton2(self):
        """Handle the DefineButton2 tag."""
        obj = _make_object("DefineButton2")
        obj.ButtonId = unpack_ui16(self._src)

        bc = BitConsumer(self._src)
        bc.ReservedFlags = bc.u_get(7)
        bc.TrackAsMenu = bc.u_get(1)

        obj.ActionOffset = unpack_ui16(self._src)

        # characters
        obj.Characters = characters = []
        while True:
            end_flag = unpack_ui8(self._src)
            if end_flag == 0:
                # all done
                obj.CharacterEndFlag = 0
                break

            # we have a BUTTONRECORD, let's go back the 8 bits and set the obj
            self._src.seek(-1, io.SEEK_CUR)
            character = _make_object("ButtonRecord")
            characters.append(character)

            bc = BitConsumer(self._src)
            character.ButtonReserved = bc.u_get(2)
            character.ButtonHasBlendMode = bc.u_get(1)
            character.ButtonHasFilterList = bc.u_get(1)
            character.ButtonStateHitTest = bc.u_get(1)
            character.ButtonStateDown = bc.u_get(1)
            character.ButtonStateOver = bc.u_get(1)
            character.ButtonStateUp = bc.u_get(1)

            character.CharacterId = unpack_ui16(self._src)
            character.PlaceDepth = unpack_ui16(self._src)
            character.PlaceMatrix = self._get_struct_matrix()
            character.ColorTransform = self._get_struct_cxformwithalpha()
            if character.ButtonHasFilterList:
                character.FilterList = self._get_struct_filterlist()
            if character.ButtonHasBlendMode:
                character.BlendMode = unpack_ui8(self._src)

        obj.Actions = actions = []
        still_have_actions = True
        while still_have_actions:
            end_flag = unpack_ui16(self._src)
            if end_flag == 0:
                # this is the last action, parse it and then exit
                still_have_actions = False

            bca = _make_object("ButtonCondAction")
            actions.append(bca)
            bca.CondActionSize = end_flag

            bc = BitConsumer(self._src)
            bca.CondIdleToOverDown = bc.u_get(1)
            bca.CondOutDownToIdle = bc.u_get(1)
            bca.CondOutDownToOverDown = bc.u_get(1)
            bca.CondOverDownToOutDown = bc.u_get(1)
            bca.CondOverDownToOverUp = bc.u_get(1)
            bca.CondOverUpToOverDown = bc.u_get(1)
            bca.CondOverUpToIdle = bc.u_get(1)
            bca.CondIdleToOverUp = bc.u_get(1)

            bca.CondKeyPress = bc.u_get(7)
            bca.CondOverDownToIdle = bc.u_get(1)
            bca.Actions = self._generic_action_parser()

        return obj

    def _handle_tag_enabledebugger2(self):
        """Handle the EnableDebugger2 tag."""
        obj = _make_object("EnableDebugger2")
        obj.Reserved = unpack_ui16(self._src)
        obj.Password = self._get_struct_string()
        return obj

    def _handle_tag_scriptlimits(self):
        """Handle the ScriptLimits tag."""
        obj = _make_object("ScriptLimits")
        obj.MaxRecursionDepth = unpack_ui16(self._src)
        obj.ScriptTimeoutSeconds = unpack_ui16(self._src)
        return obj

    def _handle_tag_framelabel(self):
        """Handle the FrameLabel tag."""
        obj = _make_object("FrameLabel")
        obj.Name = self._get_struct_string()
        return obj

    def _handle_tag_jpegtables(self):
        """Handle the JPEGTables tag."""
        obj = _make_object("JPEGTables")
        assert self._src.read(2) == b'\xFF\xD8'  # SOI marker
        eoimark1 = eoimark2 = None
        allbytes = [b'\xFF\xD8']
        while not (eoimark1 == b'\xFF' and eoimark2 == b'\xD9'):
            newbyte = self._src.read(1)
            allbytes.append(newbyte)
            eoimark1 = eoimark2
            eoimark2 = newbyte

        # concatenate everything, removing the end mark
        obj.JPEGData = b"".join(allbytes[:-2])
        return obj

    def _handle_tag_definefontalignzones(self):
        """Handle the DefineFontAlignZones tag."""
        obj = _make_object("DefineFontAlignZones")
        obj.FontId = unpack_ui16(self._src)
        bc = BitConsumer(self._src)
        obj.CSMTableHint = bc.u_get(2)
        obj.Reserved = bc.u_get(6)

        obj.ZoneTable = zone_records = []
        glyph_count = self._last_defined_glyphs_quantity
        self._last_defined_glyphs_quantity = None
        for _ in range(glyph_count):
            zone_record = _make_object("ZoneRecord")
            zone_records.append(zone_record)
            zone_record.NumZoneData = unpack_ui8(self._src)
            zone_record.ZoneData = zone_data = []
            for _ in range(zone_record.NumZoneData):
                zone_datum = _make_object("ZoneData")
                zone_data.append(zone_datum)
                zone_datum.AlignmentCoordinate = unpack_float16(self._src)
                zone_datum.Range = unpack_float16(self._src)
            bc = BitConsumer(self._src)
            zone_record.Reserved = bc.u_get(6)
            zone_record.ZoneMaskY = bc.u_get(1)
            zone_record.ZoneMaskX = bc.u_get(1)
        return obj

    def _handle_tag_definefontname(self):
        """Handle the DefineFontName tag."""
        obj = _make_object("DefineFontName")
        obj.FontId = unpack_ui16(self._src)
        obj.FontName = self._get_struct_string()
        obj.FontCopyright = self._get_struct_string()
        return obj

    def _handle_tag_csmtextsettings(self):
        """Handle the CSMTextSettings tag."""
        obj = _make_object("CSMTextSettings")
        obj.TextId = unpack_ui16(self._src)
        bc = BitConsumer(self._src)
        obj.UseFlashType = bc.u_get(2)
        obj.GridFit = bc.u_get(3)
        obj.Reserved1 = bc.u_get(3)
        obj.Thickness = unpack_float(self._src)
        obj.Sharpness = unpack_float(self._src)
        obj.Reserved2 = unpack_ui8(self._src)
        return obj

    def _get_struct_rect(self):
        """Get the RECT structure."""
        bc = BitConsumer(self._src)
        nbits = bc.u_get(5)
        return tuple(bc.u_get(nbits) for _ in range(4))

    def _get_struct_rgb(self):
        """Get the RGB structure."""
        return [unpack_ui8(self._src) for _ in range(3)]

    def _get_struct_rgba(self):
        """Get the RGBA structure."""
        return [unpack_ui8(self._src) for _ in range(4)]

    def _get_struct_langcode(self):
        """Get the LANGCODE structure."""
        code = unpack_ui8(self._src)
        return LANGCODES[code]

    def _get_struct_kerningrecord(self, font_flags_wide_codes):
        """Get the KERNINGRECORD structure."""
        getter = unpack_ui16 if font_flags_wide_codes else unpack_ui8
        data = {}
        data['FontKerningCode1'] = getter(self._src)
        data['FontKerningCode2'] = getter(self._src)
        data['FontKerningAdjustment'] = unpack_si16(self._src)
        return data

    def _get_struct_clipactions(self):
        """Get the several CLIPACTIONRECORDs."""
        obj = _make_object("ClipActions")

        # In SWF 5 and earlier, these are 2 bytes wide; in SWF 6
        # and later 4 bytes
        clipeventflags_size = 2 if self._version <= 5 else 4
        clipactionend_size = 2 if self._version <= 5 else 4
        all_zero = b"\x00" * clipactionend_size

        assert unpack_ui16(self._src) == 0  # reserved
        obj.AllEventFlags = self._src.read(clipeventflags_size)

        obj.ClipActionRecords = records = []
        while True:
            next_bytes = self._src.read(clipactionend_size)
            if next_bytes == all_zero:
                # was the ClipActionEndFlag
                return

            record = _make_object("ClipActionRecord")
            records.append(record)

            # as event flags and end flag has same size, we can do this trick
            record.EventFlags = next_bytes
            record.ActionRecordSize = unpack_ui32(self._src)
            record.TheRestTODO = self._src.read(record.ActionRecordSize)

            # FIXME: this struct needs more work; the EventFlags should be
            # expanded and each ActionRecord(s) should be detailed more
        return obj

    def _get_struct_string(self):
        """Get the STRING structure."""
        data = []
        while True:
            t = self._src.read(1)
            if t == b'\x00':
                break
            data.append(t)
        val = b''.join(data)
        return val.decode("utf8")

    def _get_struct_matrix(self):
        """Get the values for the MATRIX record."""
        obj = _make_object("Matrix")
        bc = BitConsumer(self._src)

        # scale
        obj.HasScale = bc.u_get(1)
        if obj.HasScale:
            obj.NScaleBits = n_scale_bits = bc.u_get(5)
            obj.ScaleX = bc.u_get(n_scale_bits)
            obj.ScaleY = bc.u_get(n_scale_bits)

        # rotate
        obj.HasRotate = bc.u_get(1)
        if obj.HasRotate:
            obj.NRotateBits = n_rotate_bits = bc.u_get(5)
            obj.RotateSkew0 = bc.u_get(n_rotate_bits)
            obj.RotateSkew1 = bc.u_get(n_rotate_bits)

        # translate
        obj.NTranslateBits = n_translate_bits = bc.u_get(5)
        obj.TranslateX = bc.u_get(n_translate_bits)
        obj.TranslateY = bc.u_get(n_translate_bits)
        return obj

    def _get_struct_cxformwithalpha(self):
        """Get the values for the CXFORMWITHALPHA record."""
        obj = _make_object("CXformWithAlpha")
        bc = BitConsumer(self._src)

        obj.HasAddTerms = bc.u_get(1)
        obj.HasMultTerms = bc.u_get(1)
        obj.NBits = nbits = bc.u_get(4)

        if obj.HasMultTerms:
            obj.RedMultTerm = bc.u_get(nbits)
            obj.GreenMultTerm = bc.u_get(nbits)
            obj.BlueMultTerm = bc.u_get(nbits)
            obj.AlphaMultTerm = bc.u_get(nbits)

        if obj.HasAddTerms:
            obj.RedAddTerm = bc.u_get(nbits)
            obj.GreenAddTerm = bc.u_get(nbits)
            obj.BlueAddTerm = bc.u_get(nbits)
            obj.AlphaAddTerm = bc.u_get(nbits)

        return obj

    def _get_shaperecords(self, num_fill_bits,
                          num_line_bits, shape_number):
        """Return an array of SHAPERECORDS."""
        shape_records = []
        bc = BitConsumer(self._src)

        while True:
            type_flag = bc.u_get(1)
            if type_flag:
                # edge record
                straight_flag = bc.u_get(1)
                num_bits = bc.u_get(4)
                if straight_flag:
                    record = _make_object('StraightEdgeRecord')
                    record.TypeFlag = 1
                    record.StraightFlag = 1
                    record.NumBits = num_bits
                    record.GeneralLineFlag = general_line_flag = bc.u_get(1)
                    if general_line_flag:
                        record.DeltaX = bc.s_get(num_bits + 2)
                        record.DeltaY = bc.s_get(num_bits + 2)
                    else:
                        record.VertLineFlag = vert_line_flag = bc.s_get(1)
                        if vert_line_flag:
                            record.DeltaY = bc.s_get(num_bits + 2)
                        else:
                            record.DeltaX = bc.s_get(num_bits + 2)
                else:
                    record = _make_object('CurvedEdgeRecord')
                    record.TypeFlag = 1
                    record.StraightFlag = 0
                    record.NumBits = num_bits
                    record.ControlDeltaX = bc.s_get(num_bits + 2)
                    record.ControlDeltaY = bc.s_get(num_bits + 2)
                    record.AnchorDeltaX = bc.s_get(num_bits + 2)
                    record.AnchorDeltaY = bc.s_get(num_bits + 2)

            else:
                # non edge record
                record = _make_object('StyleChangeRecord')
                record.TypeFlag = 0

                five_bits = [bc.u_get(1) for _ in range(5)]
                if not any(five_bits):
                    # the five bits are zero, this is an EndShapeRecord
                    break

                # we're not done, store the proper flags
                (record.StateNewStyles, record.StateLineStyle,
                    record.StateFillStyle1, record.StateFillStyle0,
                    record.StateMoveTo) = five_bits

                if record.StateMoveTo:
                    record.MoveBits = move_bits = bc.u_get(5)
                    record.MoveDeltaX = bc.s_get(move_bits)
                    record.MoveDeltaY = bc.s_get(move_bits)
                if record.StateFillStyle0:
                    record.FillStyle0 = bc.u_get(num_fill_bits)
                if record.StateFillStyle1:
                    record.FillStyle1 = bc.u_get(num_fill_bits)
                if record.StateLineStyle:
                    record.LineStyle = bc.u_get(num_line_bits)

                if record.StateNewStyles:
                    record.FillStyles = self._get_struct_fillstylearray(
                        shape_number)
                    record.LineStyles = self._get_struct_linestylearray(
                        shape_number)
                    # these two not only belong to the record, but also
                    # modifies the number of bits read in the future
                    # if shape number bigs enough (didn't find this in the
                    # spec, but works for now, maybe '2' is not the limit...)
                    if shape_number > 2:
                        record.NumFillBits = num_fill_bits = bc.u_get(4)
                        record.NumLineBits = num_line_bits = bc.u_get(4)
                    else:
                        record.NumFillBits = bc.u_get(4)
                        record.NumLineBits = bc.u_get(4)

                    # reset the BC here, as the structures just read work at
                    # byte level
                    bc = BitConsumer(self._src)

            shape_records.append(record)
        return shape_records

    def _get_struct_shape(self):
        """Get the values for the SHAPE record."""
        obj = _make_object("Shape")
        bc = BitConsumer(self._src)
        obj.NumFillBits = n_fill_bits = bc.u_get(4)
        obj.NumLineBits = n_line_bits = bc.u_get(4)
        obj.ShapeRecords = self._get_shaperecords(
            n_fill_bits, n_line_bits, 0)
        return obj

    def _get_struct_fillstyle(self, shape_number):
        """Get the values for the FILLSTYLE record."""
        obj = _make_object("FillStyle")
        obj.FillStyleType = style_type = unpack_ui8(self._src)

        if style_type == 0x00:
            if shape_number <= 2:
                obj.Color = self._get_struct_rgb()
            else:
                obj.Color = self._get_struct_rgba()

        if style_type in (0x10, 0x12, 0x13):
            obj.GradientMatrix = self._get_struct_matrix()

        if style_type in (0x10, 0x12):
            obj.Gradient = self._get_struct_gradient(shape_number)
        if style_type == 0x13:
            obj.Gradient = self._get_struct_focalgradient(shape_number)

        if style_type in (0x40, 0x41, 0x42, 0x43):
            obj.BitmapId = unpack_ui16(self._src)
            obj.BitmapMatrix = self._get_struct_matrix()
        return obj

    def _get_struct_fillstylearray(self, shape_number):
        """Get the values for the FILLSTYLEARRAY record."""
        obj = _make_object("FillStyleArray")
        obj.FillStyleCount = count = unpack_ui8(self._src)
        if count == 0xFF:
            obj.FillStyleCountExtended = count = unpack_ui16(self._src)
        obj.FillStyles = [self._get_struct_fillstyle(shape_number)
                          for _ in range(count)]
        return obj

    def _get_struct_linestylearray(self, shape_number):
        """Get the values for the LINESTYLEARRAY record."""
        obj = _make_object("LineStyleArray")
        obj.LineStyleCount = count = unpack_ui8(self._src)
        if count == 0xFF:
            obj.LineStyleCountExtended = count = unpack_ui16(self._src)
        obj.LineStyles = line_styles = []

        for _ in range(count):
            if shape_number <= 3:
                record = _make_object("LineStyle")
                record.Width = unpack_ui16(self._src)
                if shape_number <= 2:
                    record.Color = self._get_struct_rgb()
                else:
                    record.Color = self._get_struct_rgba()
            else:
                record = _make_object("LineStyle2")
                record.Width = unpack_ui16(self._src)

                bc = BitConsumer(self._src)
                record.StartCapStyle = bc.u_get(2)
                record.JoinStyle = bc.u_get(2)
                record.HasFillFlag = bc.u_get(1)
                record.NoHScaleFlag = bc.u_get(1)
                record.NoVScaleFlag = bc.u_get(1)
                record.PixelHintingFlag = bc.u_get(1)

                bc.u_get(5)  # reserved
                record.NoClose = bc.u_get(1)
                record.EndCapStyle = bc.u_get(2)

                if record.JoinStyle == 2:
                    record.MiterLimitFactor = unpack_ui16(self._src)
                if record.HasFillFlag == 0:
                    record.Color = self._get_struct_rgba()
                else:
                    record.Color = self._get_struct_fillstyle(shape_number)

            line_styles.append(record)

        return obj

    def _get_struct_encodedu32(self):
        """Get a EncodedU32 number."""
        useful = []
        while True:
            byte = ord(self._src.read(1))
            useful.append(byte)
            if byte < 127:
                # got all the useful bytes
                break

        # transform into bits reordering the bytes
        useful = ['00000000' + bin(b)[2:] for b in useful[::-1]]

        # get the top 7 (*seven*, as the eight one is the flag) and convert
        return int(''.join([b[-7:] for b in useful]), 2)

    def _get_struct_shapewithstyle(self, shape_number):
        """Get the values for the SHAPEWITHSTYLE record."""
        obj = _make_object("ShapeWithStyle")
        obj.FillStyles = self._get_struct_fillstylearray(shape_number)
        obj.LineStyles = self._get_struct_linestylearray(shape_number)
        bc = BitConsumer(self._src)
        obj.NumFillBits = n_fill_bits = bc.u_get(4)
        obj.NumlineBits = n_line_bits = bc.u_get(4)
        obj.ShapeRecords = self._get_shaperecords(
            n_fill_bits, n_line_bits, shape_number)
        return obj

    def _get_struct_gradient(self, shape_number):
        """Get the values for the GRADIENT record."""
        obj = _make_object("Gradient")
        bc = BitConsumer(self._src)
        obj.SpreadMode = bc.u_get(2)
        obj.InterpolationMode = bc.u_get(2)
        obj.NumGradients = bc.u_get(4)
        obj.GradientRecords = gradient_records = []

        for _ in range(obj.NumGradients):
            record = _make_object("GradRecord")
            gradient_records.append(record)
            record.Ratio = unpack_ui8(self._src)
            if shape_number <= 2:
                record.Color = self._get_struct_rgb()
            else:
                record.Color = self._get_struct_rgba()
        return obj

    def _get_struct_focalgradient(self, shape_number):
        """Get the values for the FOCALGRADIENT record."""
        obj = _make_object("FocalGradient")
        bc = BitConsumer(self._src)
        obj.SpreadMode = bc.u_get(2)
        obj.InterpolationMode = bc.u_get(2)
        obj.NumGradients = bc.u_get(4)
        obj.GradientRecords = gradient_records = []

        for _ in range(obj.NumGradients):
            record = _make_object("GradRecord")
            gradient_records.append(record)
            record.Ratio = unpack_ui8(self._src)
            if shape_number <= 2:
                record.Color = self._get_struct_rgb()
            else:
                record.Color = self._get_struct_rgba()

        obj.FocalPoint = unpack_fixed8(self._src)
        return obj

    def _get_struct_filterlist(self):
        """Get the values for the FILTERLIST record."""
        obj = _make_object("FilterList")
        obj.NumberOfFilters = unpack_ui8(self._src)
        obj.Filter = filters = []
        # how to decode each filter type (and name), according to the filter id
        filter_type = [
            ("DropShadowFilter", self._get_struct_dropshadowfilter),  # 0
            ("BlurFilter", self._get_struct_blurfilter),  # 1
            ("GlowFilter", self._get_struct_glowfilter),  # 2...
            ("BevelFilter", self._get_struct_bevelfilter),
            ("GradientGlowFilter", self._get_struct_gradientglowfilter),
            ("ConvolutionFilter", self._get_struct_convolutionfilter),
            ("ColorMatrixFilter", self._get_struct_colormatrixfilter),
            ("GradientBevelFilter", self._get_struct_gradientbevelfilter),  # 7
        ]

        for _ in range(obj.NumberOfFilters):
            _filter = _make_object("Filter")
            filters.append(_filter)

            _filter.FilterId = unpack_ui8(self._src)
            name, func = filter_type[_filter.FilterId]
            setattr(_filter, name, func())

    def _get_struct_dropshadowfilter(self):
        """Get the values for the DROPSHADOWFILTER record."""
        obj = _make_object("DropShadowFilter")
        obj.DropShadowColor = self._get_struct_rgba()
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        obj.Angle = unpack_fixed16(self._src)
        obj.Distance = unpack_fixed16(self._src)
        obj.Strength = unpack_fixed8(self._src)
        bc = BitConsumer(self._src)
        obj.InnerShadow = bc.u_get(1)
        obj.Knockout = bc.u_get(1)
        obj.CompositeSource = bc.u_get(1)
        obj.Passes = bc.u_get(5)
        return obj

    def _get_struct_blurfilter(self):
        """Get the values for the BLURFILTER record."""
        obj = _make_object("BlurFilter")
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        bc = BitConsumer(self._src)
        obj.Passes = bc.u_get(5)
        obj.Reserved = bc.u_get(3)
        return obj

    def _get_struct_glowfilter(self):
        """Get the values for the GLOWFILTER record."""
        obj = _make_object("GlowFilter")
        obj.GlowColor = self._get_struct_rgba()
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        obj.Strength = unpack_fixed8(self._src)
        bc = BitConsumer(self._src)
        obj.InnerGlow = bc.u_get(1)
        obj.Knockout = bc.u_get(1)
        obj.CompositeSource = bc.u_get(1)
        obj.Passes = bc.u_get(5)
        return obj

    def _get_struct_bevelfilter(self):
        """Get the values for the BEVELFILTER record."""
        obj = _make_object("BevelFilter")
        obj.ShadowColor = self._get_struct_rgba()
        obj.HighlightColor = self._get_struct_rgba()
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        obj.Angle = unpack_fixed16(self._src)
        obj.Distance = unpack_fixed16(self._src)
        obj.Strength = unpack_fixed8(self._src)
        bc = BitConsumer(self._src)
        obj.InnerShadow = bc.u_get(1)
        obj.Knockout = bc.u_get(1)
        obj.CompositeSource = bc.u_get(1)
        obj.OnTop = bc.u_get(1)
        obj.Passes = bc.u_get(4)
        return obj

    def _get_struct_gradientglowfilter(self):
        """Get the values for the GRADIENTGLOWFILTER record."""
        obj = _make_object("GradientBevelFilter")
        obj.NumColors = num_colors = unpack_ui8(self._src)
        obj.GradientColors = [self._get_struct_rgba()
                              for _ in range(num_colors)]
        obj.GradientRatio = [unpack_ui8(self._src)
                             for _ in range(num_colors)]
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        obj.Angle = unpack_fixed16(self._src)
        obj.Distance = unpack_fixed16(self._src)
        obj.Strength = unpack_fixed8(self._src)
        bc = BitConsumer(self._src)
        obj.InnerShadow = bc.u_get(1)
        obj.Knockout = bc.u_get(1)
        obj.CompositeSource = bc.u_get(1)
        obj.OnTop = bc.u_get(1)
        obj.Passes = bc.u_get(4)
        return obj

    def _get_struct_convolutionfilter(self):
        """Get the values for the CONVOLUTIONFILTER record."""
        obj = _make_object("ConvolutionFilter")
        obj.MatrixX = unpack_ui8(self._src)
        obj.MatrixY = unpack_ui8(self._src)
        obj.Divisor = unpack_float(self._src)
        obj.Bias = unpack_float(self._src)

        _quant = obj.MatrixX * obj.MatrixY
        obj.Matrix = [unpack_float(self._src) for _ in range(_quant)]

        obj.DefaultColor = self._get_struct_rgba()
        bc = BitConsumer(self._src)
        obj.Reserved = bc.u_get(6)
        obj.Clamp = bc.u_get(1)
        obj.PreserveAlpha = bc.u_get(1)
        return obj

    def _get_struct_colormatrixfilter(self):
        """Get the values for the COLORMATRIXFILTER record."""
        obj = _make_object("ColorMatrixFilter")
        obj.Matrix = [unpack_float(self._src) for _ in range(20)]
        return obj

    def _get_struct_gradientbevelfilter(self):
        """Get the values for the GRADIENTBEVELFILTER record."""
        obj = _make_object("GradientBevelFilter")
        obj.NumColors = num_colors = unpack_ui8(self._src)
        obj.GradientColors = [self._get_struct_rgba()
                              for _ in range(num_colors)]
        obj.GradientRatio = [unpack_ui8(self._src)
                             for _ in range(num_colors)]
        obj.BlurX = unpack_fixed16(self._src)
        obj.BlurY = unpack_fixed16(self._src)
        obj.Angle = unpack_fixed16(self._src)
        obj.Distance = unpack_fixed16(self._src)
        obj.Strength = unpack_fixed8(self._src)
        bc = BitConsumer(self._src)
        obj.InnerShadow = bc.u_get(1)
        obj.Knockout = bc.u_get(1)
        obj.CompositeSource = bc.u_get(1)
        obj.OnTop = bc.u_get(1)
        obj.Passes = bc.u_get(4)
        return obj

    def _handle_actionconstantpool(self, _):
        """Handle the ActionConstantPool action."""
        obj = _make_object("ActionConstantPool")
        obj.Count = count = unpack_ui16(self._src)
        obj.ConstantPool = pool = []
        for _ in range(count):
            pool.append(self._get_struct_string())
        yield obj

    def _handle_actiongeturl(self, _):
        """Handle the ActionGetURL action."""
        obj = _make_object("ActionGetURL")
        obj.UrlString = self._get_struct_string()
        obj.TargetString = self._get_struct_string()
        yield obj

    def _handle_actionpush(self, length):
        """Handle the ActionPush action."""
        init_pos = self._src.tell()
        while self._src.tell() < init_pos + length:
            obj = _make_object("ActionPush")
            obj.Type = unpack_ui8(self._src)
            # name and how to read each type
            push_types = {
                0: ("String", self._get_struct_string),
                1: ("Float", lambda: unpack_float(self._src)),
                2: ("Null", lambda: None),
                4: ("RegisterNumber", lambda: unpack_ui8(self._src)),
                5: ("Boolean", lambda: unpack_ui8(self._src)),
                6: ("Double", lambda: unpack_double(self._src)),
                7: ("Integer", lambda: unpack_ui32(self._src)),
                8: ("Constant8", lambda: unpack_ui8(self._src)),
                9: ("Constant16", lambda: unpack_ui16(self._src)),
            }
            name, func = push_types[obj.Type]
            setattr(obj, name, func())
            yield obj

    def _handle_actiondefinefunction(self, _):
        """Handle the ActionDefineFunction action."""
        obj = _make_object("ActionDefineFunction")
        obj.FunctionName = self._get_struct_string()
        obj.NumParams = unpack_ui16(self._src)
        for i in range(1, obj.NumParams + 1):
            setattr(obj, "param" + str(i), self._get_struct_string())
        obj.CodeSize = unpack_ui16(self._src)
        yield obj

    def _handle_actionif(self, _):
        """Handle the ActionIf action."""
        obj = _make_object("ActionIf")
        obj.BranchOffset = unpack_si16(self._src)
        yield obj

    def _handle_actiondefinefunction2(self, _):
        """Handle the ActionDefineFunction2 action."""
        obj = _make_object("ActionDefineFunction2")
        obj.FunctionName = self._get_struct_string()
        obj.NumParams = unpack_ui16(self._src)
        obj.RegisterCount = unpack_ui8(self._src)
        bc = BitConsumer(self._src)
        obj.PreloadParentFlag = bc.u_get(1)
        obj.PreloadRootFlag = bc.u_get(1)
        obj.SupressSuperFlag = bc.u_get(1)
        obj.PreloadSuperFlag = bc.u_get(1)
        obj.SupressArgumentsFlag = bc.u_get(1)
        obj.PreloadArgumentsFlag = bc.u_get(1)
        obj.SupressThisFlag = bc.u_get(1)
        obj.PreloadThisFlag = bc.u_get(1)
        obj.Reserved = bc.u_get(7)
        obj.PreloadGlobalFlag = bc.u_get(1)
        obj.Parameters = parameters = []
        for _ in range(obj.NumParams):
            parameter = _make_object("Parameter")
            parameters.append(parameter)
            parameter.Register = unpack_ui8(self._src)
            parameter.ParamName = self._get_struct_string()
        obj.CodeSize = unpack_ui16(self._src)
        yield obj

    def coverage(self):
        """Calculate the coverage of a file."""
        items_unk = collections.Counter()
        items_ok = collections.Counter()

        def _go_deep(obj):
            """Recursive function to find internal attributes."""
            if type(obj).__name__ in ('UnknownObject', 'UnknownAction'):
                # blatantly unknown
                items_unk[obj.name] += 1
            elif obj.name in ('DefineMorphShape2', 'ClipActions'):
                # these are incomplete, see FIXMEs in the code above
                items_unk[obj.name] += 1
            else:
                # fully parsed
                items_ok[obj.name] += 1

            for name in obj._attribs:
                attr = getattr(obj, name)
                if isinstance(attr, SWFObject):
                    _go_deep(attr)

        for tag in self.tags:
            _go_deep(tag)

        full_count = sum(items_ok.values()) + sum(items_unk.values())
        coverage = 100 * sum(items_ok.values()) / full_count
        print("Coverage is {:.1f}% of {} total items".format(coverage,
                                                             full_count))
        print("Most common parsed objects:")
        for k, v in items_ok.most_common(3):
            print("{:5d} {}".format(v, k))
        if items_unk:
            print("Most common Unknown objects")
            for k, v in items_unk.most_common(3):
                print("{:5d} {}".format(v, k))


def parsefile(filename):
    """Parse a SWF.

    If you have a file object already, just use SWFParser directly.
    """
    with open(filename, 'rb') as fh:
        return SWFParser(fh)
