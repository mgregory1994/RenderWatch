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


class TestNvencNonRefP(unittest.TestCase):
    """Tests all Non Ref P option values for the H264 and HEVC NVENC codecs."""

    def test_non_ref_p(self):
        """Tests the Non Ref P option values for the H264 and HEVC NVENC codecs."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_non_ref_p_normal_values(h264_nvenc, hevc_nvenc)
        self._test_non_ref_p_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_non_ref_p_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.non_ref_p = True
        hevc_nvenc.non_ref_p = True
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = False
        hevc_nvenc.non_ref_p = False
        self.assertFalse(h264_nvenc.non_ref_p)
        self.assertFalse(hevc_nvenc.non_ref_p)

    def _test_non_ref_p_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.non_ref_p = -1
        hevc_nvenc.non_ref_p = -1
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = -10
        hevc_nvenc.non_ref_p = -10
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = 0
        hevc_nvenc.non_ref_p = 0
        self.assertFalse(h264_nvenc.non_ref_p)
        self.assertFalse(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = 1
        hevc_nvenc.non_ref_p = 1
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = 10
        hevc_nvenc.non_ref_p = 10
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = 'Hello, World!'
        hevc_nvenc.non_ref_p = 'Hello, World!'
        self.assertTrue(h264_nvenc.non_ref_p)
        self.assertTrue(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = ''
        hevc_nvenc.non_ref_p = ''
        self.assertFalse(h264_nvenc.non_ref_p)
        self.assertFalse(hevc_nvenc.non_ref_p)
        h264_nvenc.non_ref_p = None
        hevc_nvenc.non_ref_p = None
        self.assertFalse(h264_nvenc.non_ref_p)
        self.assertFalse(hevc_nvenc.non_ref_p)


if __name__ == '__main__':
    unittest.main()
