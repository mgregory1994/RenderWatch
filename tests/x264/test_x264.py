# Copyright 2021 Michael Gregory
#
# This file is part of Render Watch.
#
# Render Watch is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Render Watch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Render Watch.  If not, see <https://www.gnu.org/licenses/>.


import unittest

from render_watch.ffmpeg.x264 import X264


class TestX264(unittest.TestCase):
    """Tests all X264 initial options."""

    def test_instantiation(self):
        """Tests the initial values of the X264 codec."""
        x264 = X264()
        self.assertEqual(x264.codec_name, 'libx264')
        self.assertEqual(x264.crf, 20.0)
        self.assertIsNone(x264.qp)
        self.assertIsNone(x264.bitrate)
        self.assertEqual(x264.profile, 0)
        self.assertEqual(x264.preset, 0)
        self.assertEqual(x264.level, 0)
        self.assertEqual(x264.tune, 0)
        self.assertFalse(x264.advanced_enabled)
        self.assertEqual(x264.keyint, 250)
        self.assertEqual(x264.min_keyint, 25)
        self.assertIsNone(x264.scenecut)
        self.assertEqual(x264.bframes, 3)
        self.assertEqual(x264.b_adapt, 0)
        self.assertEqual(x264.b_pyramid, 0)
        self.assertFalse(x264.no_cabac)
        self.assertEqual(x264.ref, 3)
        self.assertFalse(x264.no_deblock)
        self.assertTupleEqual(x264.deblock, (0, 0))
        self.assertEqual(x264.vbv_maxrate, 2500)
        self.assertEqual(x264.vbv_bufsize, 2500)
        self.assertEqual(x264.aq_mode, 0)
        self.assertEqual(x264.aq_strength, 1.0)
        self.assertIsNone(x264.encode_pass)
        self.assertIsNone(x264.stats)
        self.assertIsNone(x264.partitions)
        self.assertEqual(x264.direct, 0)
        self.assertFalse(x264.weightb)
        self.assertEqual(x264.me, 0)
        self.assertEqual(x264.me_range, 16)
        self.assertEqual(x264.subme, 0)
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))
        self.assertFalse(x264.mixed_refs)
        self.assertFalse(x264.dct8x8)
        self.assertEqual(x264.trellis, 0)
        self.assertFalse(x264.no_fast_pskip)
        self.assertFalse(x264.no_dct_decimate)
        self.assertFalse(x264.constant_bitrate)
        self.assertEqual(x264.weightp, 0)
        self.assertIsNone(x264.get_ffmpeg_advanced_args()['-x264-params'])


if __name__ == '__main__':
    unittest.main()
