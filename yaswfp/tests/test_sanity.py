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

import os
import unittest

from yaswfp.swfparser import SWFParser, parsefile

BASEDIR = os.path.join(os.path.dirname(__file__), 'samples')


def _get_attribs(tag):
    """Get the attribs of a tag."""
    return {x for x in dir(tag) if x[0].isupper()}


class SanityTestCase(unittest.TestCase):

    def test_1252533834(self):
        SWFParser.unknown_alert = True
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
