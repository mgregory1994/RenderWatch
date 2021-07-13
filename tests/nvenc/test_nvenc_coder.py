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


class TestNvencCoder(unittest.TestCase):
    """Tests all Coder option values for the H264 NVENC codec."""

    def test_coder(self):
        """Tests the Coder option values for the H264 NVENC codec."""
        h264_nvenc = H264Nvenc()
        self._test_coder_normal_values(h264_nvenc)
        self._test_coder_abnormal_values(h264_nvenc)

    def _test_coder_normal_values(self, h264_nvenc):
        # Values that should apply.
        h264_nvenc.coder = 0
        self.assertEqual(h264_nvenc.coder, 0)
        h264_nvenc.coder = 1
        self.assertEqual(h264_nvenc.coder, 1)
        h264_nvenc.coder = H264Nvenc.CODER_LIST_LENGTH - 1
        self.assertEqual(h264_nvenc.coder, H264Nvenc.CODER_LIST_LENGTH - 1)

    def _test_coder_abnormal_values(self, h264_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.coder = -1
        self.assertEqual(h264_nvenc.coder, 0)
        h264_nvenc.coder = H264Nvenc.CODER_LIST_LENGTH * -1
        self.assertEqual(h264_nvenc.coder, 0)
        h264_nvenc.coder = H264Nvenc.CODER_LIST_LENGTH
        self.assertEqual(h264_nvenc.coder, 0)
        h264_nvenc.coder = None
        self.assertEqual(h264_nvenc.coder, 0)


if __name__ == '__main__':
    unittest.main()
