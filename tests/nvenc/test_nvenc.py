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

from render_watch.ffmpeg.h264_nvenc import H264Nvenc
from render_watch.ffmpeg.hevc_nvenc import HevcNvenc


class TestNvenc(unittest.TestCase):
    """Tests all NVENC initial options."""

    def test_instantiation(self):
        """Tests the initial values of H264 and HEVC NVENC objects."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self.assertEqual(h264_nvenc.codec_name, 'h264_nvenc')
        self.assertEqual(hevc_nvenc.codec_name, 'hevc_nvenc')
        self.assertFalse(h264_nvenc.advanced_enabled)
        self.assertFalse(hevc_nvenc.advanced_enabled)
        self.assertFalse(h264_nvenc.qp_custom_enabled)
        self.assertFalse(hevc_nvenc.qp_custom_enabled)
        self.assertFalse(h264_nvenc.dual_pass_enabled)
        self.assertFalse(hevc_nvenc.dual_pass_enabled)
        self.assertEqual(h264_nvenc.qp, 20.0)
        self.assertEqual(hevc_nvenc.qp, 20.0)
        self.assertIsNone(h264_nvenc.bitrate)
        self.assertIsNone(hevc_nvenc.bitrate)
        self.assertEqual(h264_nvenc.profile, 0)
        self.assertEqual(hevc_nvenc.profile, 0)
        self.assertEqual(h264_nvenc.preset, 0)
        self.assertEqual(hevc_nvenc.preset, 0)
        self.assertEqual(h264_nvenc.level, 0)
        self.assertEqual(hevc_nvenc.level, 0)
        self.assertEqual(h264_nvenc.tune, 0)
        self.assertEqual(hevc_nvenc.tune, 0)
        self.assertEqual(h264_nvenc.multi_pass, 0)
        self.assertEqual(hevc_nvenc.multi_pass, 0)
        self.assertFalse(h264_nvenc.cbr)
        self.assertFalse(hevc_nvenc.cbr)
        self.assertEqual(h264_nvenc.qp_i, 20.0)
        self.assertEqual(hevc_nvenc.qp_i, 20.0)
        self.assertEqual(h264_nvenc.qp_p, 20.0)
        self.assertEqual(hevc_nvenc.qp_p, 20.0)
        self.assertEqual(h264_nvenc.qp_b, 20.0)
        self.assertEqual(hevc_nvenc.qp_b, 20.0)
        self.assertEqual(h264_nvenc.rc, 0)
        self.assertEqual(hevc_nvenc.rc, 0)
        self.assertEqual(h264_nvenc.rc_lookahead, 0)
        self.assertEqual(hevc_nvenc.rc_lookahead, 0)
        self.assertEqual(h264_nvenc.surfaces, 8)
        self.assertEqual(hevc_nvenc.surfaces, 8)
        self.assertFalse(h264_nvenc.no_scenecut)
        self.assertFalse(hevc_nvenc.no_scenecut)
        self.assertFalse(h264_nvenc.forced_idr)
        self.assertFalse(hevc_nvenc.forced_idr)
        self.assertFalse(h264_nvenc.b_adapt)
        self.assertFalse(h264_nvenc.spatial_aq)
        self.assertFalse(hevc_nvenc.spatial_aq)
        self.assertFalse(h264_nvenc.temporal_aq)
        self.assertFalse(hevc_nvenc.temporal_aq)
        self.assertFalse(h264_nvenc.non_ref_p)
        self.assertFalse(hevc_nvenc.non_ref_p)
        self.assertFalse(h264_nvenc.strict_gop)
        self.assertFalse(hevc_nvenc.strict_gop)
        self.assertEqual(h264_nvenc.aq_strength, 8)
        self.assertEqual(hevc_nvenc.aq_strength, 8)
        self.assertFalse(h264_nvenc.bluray_compat)
        self.assertFalse(hevc_nvenc.bluray_compat)
        self.assertFalse(h264_nvenc.weighted_pred)
        self.assertFalse(hevc_nvenc.weighted_pred)
        self.assertEqual(h264_nvenc.coder, 0)
        self.assertEqual(h264_nvenc.b_ref_mode, 0)
        self.assertEqual(hevc_nvenc.b_ref_mode, 0)
        self.assertFalse(hevc_nvenc.tier)
        self.assertIsNone(h264_nvenc.encode_pass)
        self.assertIsNone(hevc_nvenc.encode_pass)
        self.assertIsNone(h264_nvenc.get_ffmpeg_advanced_args()[None])
        self.assertIsNone(hevc_nvenc.get_ffmpeg_advanced_args()[None])


if __name__ == '__main__':
    unittest.main()
