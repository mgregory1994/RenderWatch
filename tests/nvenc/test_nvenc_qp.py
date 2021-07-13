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


class TestNvencQP(unittest.TestCase):
    """Tests all QP option values for H264 and HEVC objects."""

    def test_qp(self):
        """Test QP values option for H264 and HEVC NVENC objects."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_qp_normal_values(h264_nvenc, hevc_nvenc)
        self._test_qp_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_qp_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.qp = 0
        hevc_nvenc.qp = 0
        self.assertEqual(h264_nvenc.qp, 0)
        self.assertEqual(hevc_nvenc.qp, 0)
        h264_nvenc.qp = 1
        hevc_nvenc.qp = 1
        self.assertEqual(h264_nvenc.qp, 1)
        self.assertEqual(hevc_nvenc.qp, 1)
        h264_nvenc.qp = 20
        hevc_nvenc.qp = 20
        self.assertEqual(h264_nvenc.qp, 20)
        self.assertEqual(hevc_nvenc.qp, 20)
        h264_nvenc.qp = 51
        hevc_nvenc.qp = 51
        self.assertEqual(h264_nvenc.qp, 51)
        self.assertEqual(hevc_nvenc.qp, 51)
        h264_nvenc.qp = 20.5
        hevc_nvenc.qp = 20.5
        self.assertEqual(h264_nvenc.qp, 20.5)
        self.assertEqual(hevc_nvenc.qp, 20.5)

    def _test_qp_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.qp = -1
        hevc_nvenc.qp = -1
        self.assertIsNone(h264_nvenc.qp)
        self.assertIsNone(hevc_nvenc.qp)
        h264_nvenc.qp = -52
        hevc_nvenc.qp = -52
        self.assertIsNone(h264_nvenc.qp)
        self.assertIsNone(hevc_nvenc.qp)
        h264_nvenc.qp = 52
        hevc_nvenc.qp = 52
        self.assertIsNone(h264_nvenc.qp)
        self.assertIsNone(hevc_nvenc.qp)
        h264_nvenc.qp = 101
        hevc_nvenc.qp = 101
        self.assertIsNone(h264_nvenc.qp)
        self.assertIsNone(hevc_nvenc.qp)
        h264_nvenc.qp = None
        hevc_nvenc.qp = None
        self.assertIsNone(h264_nvenc.qp)
        self.assertIsNone(hevc_nvenc.qp)


if __name__ == '__main__':
    unittest.main()
