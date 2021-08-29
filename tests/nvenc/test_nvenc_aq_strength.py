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


class TestNvencAQStrength(unittest.TestCase):
    """Tests all AQ Strength option values for the H264 and HEVC NVENC codecs."""

    def test_aq_strength(self):
        """Tests the AQ Strength option values for the H264 and HEVC NVENC codecs."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_aq_strength_normal_values(h264_nvenc, hevc_nvenc)
        self._test_aq_strength_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_aq_strength_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.aq_strength = 0
        hevc_nvenc.aq_strength = 0
        self.assertEqual(h264_nvenc.aq_strength, 0)
        self.assertEqual(hevc_nvenc.aq_strength, 0)
        h264_nvenc.aq_strength = 1
        hevc_nvenc.aq_strength = 1
        self.assertEqual(h264_nvenc.aq_strength, 1)
        self.assertEqual(hevc_nvenc.aq_strength, 1)
        h264_nvenc.aq_strength = 8
        hevc_nvenc.aq_strength = 8
        self.assertEqual(h264_nvenc.aq_strength, 8)
        self.assertEqual(hevc_nvenc.aq_strength, 8)
        h264_nvenc.aq_strength = 16
        hevc_nvenc.aq_strength = 16
        self.assertEqual(h264_nvenc.aq_strength, 16)
        self.assertEqual(hevc_nvenc.aq_strength, 16)
        h264_nvenc.aq_strength = 512
        hevc_nvenc.aq_strength = 512
        self.assertEqual(h264_nvenc.aq_strength, 512)
        self.assertEqual(hevc_nvenc.aq_strength, 512)

    def _test_aq_strength_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.aq_strength = -1
        hevc_nvenc.aq_strength = -1
        self.assertEqual(h264_nvenc.aq_strength, 8)
        self.assertEqual(hevc_nvenc.aq_strength, 8)
        h264_nvenc.aq_strength = -512
        hevc_nvenc.aq_strength = -512
        self.assertEqual(h264_nvenc.aq_strength, 8)
        self.assertEqual(hevc_nvenc.aq_strength, 8)
        h264_nvenc.aq_strength = None
        hevc_nvenc.aq_strength = None
        self.assertEqual(h264_nvenc.aq_strength, 8)
        self.assertEqual(hevc_nvenc.aq_strength, 8)


if __name__ == '__main__':
    unittest.main()
