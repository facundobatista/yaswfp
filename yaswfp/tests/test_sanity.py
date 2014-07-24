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

"""Some sanity checks."""

import itertools
import os
import unittest

from unittest import mock

from yaswfp.swfparser import SWFParser, parsefile

BASEDIR = os.path.join(os.path.dirname(__file__), 'samples')


def _get_attribs(tag):
    """Get the attribs of a tag."""
    return {x for x in dir(tag) if x[0].isupper()}


class SanityTestCase(unittest.TestCase):

    def test_1252533834(self):
        with mock.patch.object(SWFParser, 'unknown_alert', True):
            swf = parsefile(os.path.join(BASEDIR, '1252533834.swf'))

        # header
        h = swf.header
        self.assertEqual(h.FileLength, 4716)
        self.assertEqual(h.FrameCount, 21)
        self.assertEqual(h.FrameRate, 3840)
        self.assertEqual(h.FrameSize,  (0, 11000, 0, 8000))
        self.assertEqual(h.Signature, 'CWS')
        self.assertEqual(h.Version, 10)

        # the tags
        self.assertEqual(len(swf.tags), 55)

        t = swf.tags[0]
        self.assertEqual(t.name, 'FileAttributes')
        self.assertEqual(_get_attribs(t), {
            'UseDirectBlit', 'ActionScript3',
            'UseNetwork', 'HasMetadata', 'UseGPU'})

        t = swf.tags[1]
        self.assertEqual(t.name, 'Metadata')
        self.assertEqual(_get_attribs(t), {'Metadata'})

        t = swf.tags[2]
        self.assertEqual(t.name, 'SetBackgroundColor')
        self.assertEqual(_get_attribs(t), {'BackgroundColor'})

        t = swf.tags[3]
        self.assertEqual(t.name, 'DefineSceneAndFrameLabelData')
        self.assertEqual(_get_attribs(t), {
            'FrameLabelCount', 'Offset1', 'Name1', 'SceneCount'})

        t = swf.tags[4]
        self.assertEqual(t.name, 'DefineShape4')
        self.assertEqual(_get_attribs(t), {
            'UsesNonScalingStrokes', 'Shapes', 'UsesFillWindingRule',
            'ShapeBounds', 'EdgeBounds', 'UsesScalingStrokes', 'ShapeId'})

        t = swf.tags[5]
        self.assertEqual(t.name, 'DefineMorphShape2')
        self.assertEqual(_get_attribs(t), {
            'Offset', 'EndEdgeBounds', 'EndEdges', 'UsesNonScalingStrokes',
            'StartEdgeBounds', 'CharacterId', 'UsesScalingStrokes',
            'StartBounds', 'EndBounds'})

        t = swf.tags[6]
        self.assertEqual(t.name, 'DefineMorphShape2')
        self.assertEqual(_get_attribs(t), {
            'Offset', 'EndEdgeBounds', 'EndEdges', 'UsesNonScalingStrokes',
            'StartEdgeBounds', 'CharacterId', 'UsesScalingStrokes',
            'StartBounds', 'EndBounds'})

        t = swf.tags[7]
        self.assertEqual(t.name, 'DefineShape4')
        self.assertEqual(_get_attribs(t), {
            'UsesNonScalingStrokes', 'Shapes', 'UsesFillWindingRule',
            'ShapeBounds', 'EdgeBounds', 'UsesScalingStrokes', 'ShapeId'})

        t = swf.tags[8]
        self.assertEqual(t.name, 'DefineSprite')
        self.assertEqual(_get_attribs(t), {
            'ControlTags', 'FrameCount', 'CharacterID'})

        t = swf.tags[9]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'Matrix',
            'PlaceFlagHasRatio', 'Depth', 'PlaceFlagHasName',
            'PlaceFlagHasClipActions', 'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[10]
        self.assertEqual(t.name, 'DefineShape4')
        self.assertEqual(_get_attribs(t), {
            'UsesNonScalingStrokes', 'Shapes', 'UsesFillWindingRule',
            'ShapeBounds', 'EdgeBounds', 'UsesScalingStrokes', 'ShapeId'})

        t = swf.tags[11]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'Matrix',
            'PlaceFlagHasRatio', 'Depth', 'PlaceFlagHasName',
            'PlaceFlagHasClipActions', 'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[12]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[13]
        self.assertEqual(t.name, 'DefineShape4')
        self.assertEqual(_get_attribs(t), {
            'UsesNonScalingStrokes', 'Shapes', 'UsesFillWindingRule',
            'ShapeBounds', 'EdgeBounds', 'UsesScalingStrokes', 'ShapeId'})

        t = swf.tags[14]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[15]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[16]
        self.assertEqual(t.name, 'DefineShape4')
        self.assertEqual(_get_attribs(t), {
            'UsesNonScalingStrokes', 'Shapes', 'UsesFillWindingRule',
            'ShapeBounds', 'EdgeBounds', 'UsesScalingStrokes', 'ShapeId'})

        t = swf.tags[17]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[18]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[19]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[20]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[21]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[22]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[23]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[24]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[25]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[26]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[27]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[28]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[29]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[30]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[31]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[32]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[33]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[34]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[35]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[36]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[37]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[38]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[39]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[40]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[41]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[42]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[43]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[44]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[45]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[46]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[47]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[48]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[49]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[50]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[51]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[52]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

        t = swf.tags[53]
        self.assertEqual(t.name, 'PlaceObject2')
        self.assertEqual(_get_attribs(t), {
            'PlaceFlagHasColorTransform', 'PlaceFlagHasCharacter',
            'PlaceFlagMove', 'PlaceFlagHasMatrix', 'PlaceFlagHasRatio',
            'Depth', 'PlaceFlagHasName', 'PlaceFlagHasClipActions',
            'CharacterId', 'PlaceFlagHasClipDepth'})

        t = swf.tags[54]
        self.assertEqual(t.name, 'ShowFrame')
        self.assertEqual(_get_attribs(t), set())

    def test_malformed_swf(self):
        # it should support a non-existant tag
        swf = parsefile(os.path.join(BASEDIR, 'wivet1.swf'))

        # header
        should_tags = [
            'FileAttributes',
            'Metadata',
            'EnableDebugger2',
            'UnspecifiedObject(tag=63)',
            'ScriptLimits',
            'SetBackgroundColor',
            'UnspecifiedObject(tag=41)',
            'FrameLabel',
            'DoABC',
            'SymbolClass',
            'ShowFrame',
        ]
        for tag_name, real_tag in itertools.zip_longest(should_tags, swf.tags):
            self.assertEqual(real_tag.name, tag_name)

    def test_subscribe(self):
        with mock.patch.object(SWFParser, 'unknown_alert', True):
            swf = parsefile(os.path.join(BASEDIR, 'subscribe.swf'))
        self.assertEqual(len(swf.tags), 16)

        t = swf.tags[1]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 0)

        t = swf.tags[2]
        self.assertEqual(t.name, 'DefineFont2')
        self.assertEqual(_get_attribs(t), {
            'FontID', 'FontFlagsHasLayout', 'FontFlagsShiftJIS',
            'FontFlagsSmallText', 'FontFlagsANSI', 'FontFlagsWideOffsets',
            'FontFlagsWideCodes', 'FontFlagsItalic', 'FontFlagsBold',
            'LanguageCode', 'FontNameLen', 'FontName', 'NumGlyphs',
            'OffsetTable', 'CodeTableOffset', 'GlyphShapeTable', 'CodeTable'})

        t = swf.tags[3]
        self.assertEqual(t.name, 'DefineText')
        self.assertEqual(_get_attribs(t), {
            'CharacterID', 'TextBounds', 'TextMatrix', 'GlyphBits',
            'AdvanceBits', 'TextRecords', 'EndOfRecordsFlag'})
        self.assertEqual(len(t.TextRecords), 2)

        t = swf.tags[4]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[5]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[6]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 0)

        t = swf.tags[7]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[8]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[9]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[10]
        self.assertEqual(t.name, 'DefineShape')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 1)

        t = swf.tags[11]
        self.assertEqual(t.name, 'DefineShape2')
        self.assertEqual(_get_attribs(t), {'ShapeId', 'ShapeBounds', 'Shapes'})
        self.assertEqual(t.Shapes.FillStyles.FillStyleCount, 1)
        self.assertEqual(t.Shapes.LineStyles.LineStyleCount, 0)

    def test_dqsv(self):
        with mock.patch.object(SWFParser, 'unknown_alert', True):
            swf = parsefile(os.path.join(BASEDIR, 'dqsv1.swf'))
        self.assertEqual(len(swf.tags), 38)

        t = swf.tags[2]
        self.assertEqual(t.name, 'DoAction')
        self.assertEqual(_get_attribs(t), {'Actions', })

        t = swf.tags[4]
        self.assertEqual(t.name, 'JPEGTables')
        self.assertEqual(_get_attribs(t), {'JPEGData', })

        t = swf.tags[12]
        self.assertEqual(t.name, 'DefineFontAlignZones')
        self.assertEqual(_get_attribs(t), {
            'FontId', 'CSMTableHint', 'Reserved', 'ZoneTable'})

        t = swf.tags[15]
        self.assertEqual(t.name, 'CSMTextSettings')
        self.assertEqual(_get_attribs(t), {
            'TextId', 'UseFlashType', 'GridFit', 'Reserved1',
            'Thickness', 'Sharpness', 'Reserved2'})

        t = swf.tags[25]
        self.assertEqual(t.name, 'DefineSprite')
        obj = t.ControlTags[3]
        self.assertEqual(obj.name, 'PlaceObject3')
        self.assertEqual(_get_attribs(obj), {
            'PlaceFlagHasClipActions', 'PlaceFlagHasClipDepth',
            'PlaceFlagHasName', 'PlaceFlagHasRatio',
            'PlaceFlagHasColorTransform', 'PlaceFlagHasMatrix',
            'PlaceFlagHasCharacter', 'PlaceFlagMove', 'Reserved',
            'PlaceFlagOpaqueBackground', 'PlaceFlagHasVisible',
            'PlaceFlagHasImage', 'PlaceFlagHasClassName',
            'PlaceFlagHasCacheAsBitmap', 'PlaceFlagHasBlendMode',
            'PlaceFlagHasFilterList', 'Depth', 'CharacterId', 'Matrix',
            'SurfaceFilterList'})

        t = swf.tags[27]
        self.assertEqual(t.name, 'DefineButton2')
        bca = t.Actions[0]  # ButtonCondAction
        obj = bca.Actions[0]
        self.assertEqual(obj.name, 'ActionConstantPool')
        self.assertEqual(_get_attribs(obj), {'Count', 'ConstantPool'})
        obj = bca.Actions[1]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[2]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[3]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[4]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[5]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[6]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[7]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[8]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[9]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[10]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[11]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[12]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[13]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[14]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[15]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[16]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[17]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[18]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[19]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[20]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[21]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[22]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[23]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[24]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[25]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[26]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[27]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[28]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[29]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Double'})
        obj = bca.Actions[30]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[31]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[32]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[33]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[34]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[35]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[36]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[37]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[38]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[39]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[40]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = bca.Actions[41]
        self.assertEqual(obj.name, 'ActionCallMethod')
        self.assertEqual(_get_attribs(obj), set())
        obj = bca.Actions[42]
        self.assertEqual(obj.name, 'ActionPop')
        self.assertEqual(_get_attribs(obj), set())

        t = swf.tags[30]
        self.assertEqual(t.name, 'DefineShape3')
        self.assertEqual(_get_attribs(t), {
            'ShapeId', 'ShapeBounds', 'Shapes'})

        t = swf.tags[33]
        self.assertEqual(t.name, 'DefineSprite')
        do_action = t.ControlTags[0]
        obj = do_action.Actions[0]
        self.assertEqual(obj.name, 'ActionConstantPool')
        self.assertEqual(_get_attribs(obj), {'Count', 'ConstantPool'})
        obj = do_action.Actions[1]
        self.assertEqual(obj.name, 'ActionStop')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[2]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[3]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[4]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[5]
        self.assertEqual(obj.name, 'ActionDefineFunction')
        self.assertEqual(_get_attribs(obj), {
            'FunctionName', 'NumParams', 'CodeSize'})
        obj = do_action.Actions[6]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[7]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[8]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Boolean'})
        obj = do_action.Actions[9]
        self.assertEqual(obj.name, 'ActionEquals2')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[10]
        self.assertEqual(obj.name, 'ActionNot')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[11]
        self.assertEqual(obj.name, 'ActionIf')
        self.assertEqual(_get_attribs(obj), {'BranchOffset'})
        obj = do_action.Actions[12]
        self.assertEqual(obj.name, 'ActionPrevFrame')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[13]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[14]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[15]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[16]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[17]
        self.assertEqual(obj.name, 'ActionDefineFunction')
        self.assertEqual(_get_attribs(obj), {
            'FunctionName', 'NumParams', 'CodeSize'})
        obj = do_action.Actions[18]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[19]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Boolean'})
        obj = do_action.Actions[20]
        self.assertEqual(obj.name, 'ActionSetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[21]
        self.assertEqual(obj.name, 'ActionPlay')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[22]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[23]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[24]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[25]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[26]
        self.assertEqual(obj.name, 'ActionDefineFunction')
        self.assertEqual(_get_attribs(obj), {
            'FunctionName', 'NumParams', 'CodeSize'})
        obj = do_action.Actions[27]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[28]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Boolean'})
        obj = do_action.Actions[29]
        self.assertEqual(obj.name, 'ActionSetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[30]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[31]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[32]
        self.assertEqual(obj.name, 'ActionGetVariable')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[33]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[34]
        self.assertEqual(obj.name, 'ActionDefineFunction2')
        self.assertEqual(_get_attribs(obj), {
            'FunctionName', 'NumParams', 'RegisterCount', 'PreloadParentFlag',
            'PreloadRootFlag', 'SupressSuperFlag', 'PreloadSuperFlag',
            'SupressArgumentsFlag', 'PreloadArgumentsFlag', 'SupressThisFlag',
            'PreloadThisFlag', 'Reserved', 'PreloadGlobalFlag', 'Parameters',
            'CodeSize'})
        obj = do_action.Actions[35]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'RegisterNumber'})
        obj = do_action.Actions[36]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[37]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[38]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[39]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[40]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Integer'})
        obj = do_action.Actions[41]
        self.assertEqual(obj.name, 'ActionGreater')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[42]
        self.assertEqual(obj.name, 'ActionNot')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[43]
        self.assertEqual(obj.name, 'ActionIf')
        self.assertEqual(_get_attribs(obj), {'BranchOffset'})
        obj = do_action.Actions[44]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'RegisterNumber'})
        obj = do_action.Actions[45]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[46]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[47]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[48]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'RegisterNumber'})
        obj = do_action.Actions[49]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[50]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[51]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Constant8'})
        obj = do_action.Actions[52]
        self.assertEqual(obj.name, 'ActionGetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[53]
        self.assertEqual(obj.name, 'ActionPush')
        self.assertEqual(_get_attribs(obj), {'Type', 'Integer'})
        obj = do_action.Actions[54]
        self.assertEqual(obj.name, 'ActionSubtract')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[55]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
        obj = do_action.Actions[56]
        self.assertEqual(obj.name, 'ActionSetMember')
        self.assertEqual(_get_attribs(obj), set())
