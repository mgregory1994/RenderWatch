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

from render_watch.ffmpeg.x265 import X265


class TestX265(unittest.TestCase):
    """Tests all X265 initial options."""

    def test_instantiation(self):
        """Tests the initial values of the X265 codec."""
        x265 = X265()
        self.assertEqual(x265.codec_name, 'libx265')
        self.assertEqual(x265.crf, 20.0)
        self.assertIsNone(x265.qp)
        self.assertIsNone(x265.bitrate)
        self.assertEqual(x265.profile, 0)
        self.assertEqual(x265.preset, 0)
        self.assertEqual(x265.level, 0)
        self.assertEqual(x265.tune, 0)
        self.assertEqual(x265.vbv_maxrate, 2500)
        self.assertEqual(x265.vbv_bufsize, 2500)
        self.assertEqual(x265.aq_mode, 0)
        self.assertEqual(x265.aq_strength, 1.0)
        self.assertFalse(x265.hevc_aq)
        self.assertEqual(x265.keyint, 250)
        self.assertEqual(x265.min_keyint, 0)
        self.assertEqual(x265.ref, 3)
        self.assertEqual(x265.bframes, 4)
        self.assertEqual(x265.b_adapt, 0)
        self.assertFalse(x265.no_b_pyramid)
        self.assertFalse(x265.b_intra)
        self.assertFalse(x265.no_open_gop)
        self.assertEqual(x265.rc_lookahead, 20)
        self.assertFalse(x265.no_scenecut)
        self.assertFalse(x265.no_high_tier)
        self.assertEqual(x265.psy_rd, 2.0)
        self.assertEqual(x265.psy_rdoq, 0.0)
        self.assertEqual(x265.me, 0)
        self.assertEqual(x265.subme, 2)
        self.assertFalse(x265.weightb)
        self.assertFalse(x265.no_weightp)
        self.assertTupleEqual(x265.deblock, (0, 0))
        self.assertFalse(x265.no_deblock)
        self.assertFalse(x265.no_sao)
        self.assertFalse(x265.sao_non_deblock)
        self.assertFalse(x265.limit_sao)
        self.assertEqual(x265.selective_sao, 0)
        self.assertEqual(x265.rd, 3)
        self.assertEqual(x265.rdoq_level, 0)
        self.assertFalse(x265.rd_refine)
        self.assertEqual(x265.ctu, 0)
        self.assertEqual(x265.min_cu_size, 0)
        self.assertFalse(x265.rect)
        self.assertFalse(x265.amp)
        self.assertFalse(x265.wpp)
        self.assertFalse(x265.pmode)
        self.assertFalse(x265.pme)
        self.assertFalse(x265.uhd_bd)
        self.assertIsNone(x265.encode_pass)
        self.assertIsNone(x265.stats)
        self.assertIsNone(x265.get_ffmpeg_advanced_args()['-x265-params'])


if __name__ == '__main__':
    unittest.main()
