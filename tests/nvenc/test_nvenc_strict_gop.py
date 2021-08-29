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


class TestNvencStrictGOP(unittest.TestCase):
    """Tests all Strict GOP option values for the H264 and HEVC NVENC codecs."""

    def test_strict_gop(self):
        """Tests the Strict GOP option values for the H264 and HEVC NVENC codecs."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_strict_gop_normal_values(h264_nvenc, hevc_nvenc)
        self._test_strict_gop_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_strict_gop_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.strict_gop = True
        hevc_nvenc.strict_gop = True
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = False
        hevc_nvenc.strict_gop = False
        self.assertFalse(h264_nvenc.strict_gop)
        self.assertFalse(hevc_nvenc.strict_gop)

    def _test_strict_gop_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.strict_gop = -1
        hevc_nvenc.strict_gop = -1
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = -10
        hevc_nvenc.strict_gop = -10
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = 0
        hevc_nvenc.strict_gop = 0
        self.assertFalse(h264_nvenc.strict_gop)
        self.assertFalse(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = 1
        hevc_nvenc.strict_gop = 1
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = 10
        hevc_nvenc.strict_gop = 10
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = 'Hello, World!'
        hevc_nvenc.strict_gop = 'Hello, World!'
        self.assertTrue(h264_nvenc.strict_gop)
        self.assertTrue(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = ''
        hevc_nvenc.strict_gop = ''
        self.assertFalse(h264_nvenc.strict_gop)
        self.assertFalse(hevc_nvenc.strict_gop)
        h264_nvenc.strict_gop = None
        hevc_nvenc.strict_gop = None
        self.assertFalse(h264_nvenc.strict_gop)
        self.assertFalse(hevc_nvenc.strict_gop)


if __name__ == '__main__':
    unittest.main()
