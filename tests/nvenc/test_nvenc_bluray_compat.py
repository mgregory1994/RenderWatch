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


class TestNvencBluerayCompat(unittest.TestCase):
    """Tests all Blu-Ray Compatibility option values for the H264 and HEVC NVENC codecs."""

    def test_bluray_compat(self):
        """Tests the Blu-Ray Compatibility option values for the H264 and HEVC NVENC codecs."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_bluray_compat_normal_values(h264_nvenc, hevc_nvenc)
        self._test_bluray_compat_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_bluray_compat_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.bluray_compat = True
        hevc_nvenc.bluray_compat = True
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = False
        hevc_nvenc.bluray_compat = False
        self.assertFalse(h264_nvenc.bluray_compat)
        self.assertFalse(hevc_nvenc.bluray_compat)

    def _test_bluray_compat_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.bluray_compat = -1
        hevc_nvenc.bluray_compat = -1
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = -10
        hevc_nvenc.bluray_compat = -10
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = 0
        hevc_nvenc.bluray_compat = 0
        self.assertFalse(h264_nvenc.bluray_compat)
        self.assertFalse(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = 1
        hevc_nvenc.bluray_compat = 1
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = 10
        hevc_nvenc.bluray_compat = 10
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = 'Hello, World!'
        hevc_nvenc.bluray_compat = 'Hello, World!'
        self.assertTrue(h264_nvenc.bluray_compat)
        self.assertTrue(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = ''
        hevc_nvenc.bluray_compat = ''
        self.assertFalse(h264_nvenc.bluray_compat)
        self.assertFalse(hevc_nvenc.bluray_compat)
        h264_nvenc.bluray_compat = None
        hevc_nvenc.bluray_compat = None
        self.assertFalse(h264_nvenc.bluray_compat)
        self.assertFalse(hevc_nvenc.bluray_compat)


if __name__ == '__main__':
    unittest.main()
