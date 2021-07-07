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


class TestNvencBitrate(unittest.TestCase):
    """Tests all Bitrate option values for H264 and HEVC NVENC objects"""

    def test_bitrate(self):
        """Tests Bitrate option values for H264 and HEVC NVENC objects."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_bitrate_normal_values(h264_nvenc, hevc_nvenc)
        self._test_bitrate_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_bitrate_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.bitrate = 0
        hevc_nvenc.bitrate = 0
        self.assertEqual(h264_nvenc.bitrate, 0)
        self.assertEqual(hevc_nvenc.bitrate, 0)
        h264_nvenc.bitrate = 1
        hevc_nvenc.bitrate = 1
        self.assertEqual(h264_nvenc.bitrate, 1)
        self.assertEqual(hevc_nvenc.bitrate, 1)
        h264_nvenc.bitrate = 2500
        hevc_nvenc.bitrate = 2500
        self.assertEqual(h264_nvenc.bitrate, 2500)
        self.assertEqual(hevc_nvenc.bitrate, 2500)
        h264_nvenc.bitrate = 99999
        hevc_nvenc.bitrate = 99999
        self.assertEqual(h264_nvenc.bitrate, 99999)
        self.assertEqual(hevc_nvenc.bitrate, 99999)

    def _test_bitrate_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.bitrate = -1
        hevc_nvenc.bitrate = -1
        self.assertIsNone(h264_nvenc.bitrate)
        self.assertIsNone(hevc_nvenc.bitrate)
        h264_nvenc.bitrate = -99999
        hevc_nvenc.bitrate = -99999
        self.assertIsNone(h264_nvenc.bitrate)
        self.assertIsNone(hevc_nvenc.bitrate)
        h264_nvenc.bitrate = 100000
        hevc_nvenc.bitrate = 100000
        self.assertIsNone(h264_nvenc.bitrate)
        self.assertIsNone(hevc_nvenc.bitrate)
        h264_nvenc.bitrate = None
        hevc_nvenc.bitrate = None
        self.assertIsNone(h264_nvenc.bitrate)
        self.assertIsNone(hevc_nvenc.bitrate)


if __name__ == '__main__':
    unittest.main()
