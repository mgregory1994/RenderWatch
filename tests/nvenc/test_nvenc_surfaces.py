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


class TestNvencSurfaces(unittest.TestCase):
    """Tests all Surfaces option values for the H264 and HEVC NVENC codecs."""

    def test_something(self):
        """Tests the Surfaces option values for the H264 and HEVC NVENC codecs."""
        h264_nvenc = H264Nvenc()
        hevc_nvenc = HevcNvenc()
        self._test_surfaces_normal_values(h264_nvenc, hevc_nvenc)
        self._test_surfaces_abnormal_values(h264_nvenc, hevc_nvenc)

    def _test_surfaces_normal_values(self, h264_nvenc, hevc_nvenc):
        # Values that should apply.
        h264_nvenc.surfaces = 0
        hevc_nvenc.surfaces = 0
        self.assertEqual(h264_nvenc.surfaces, 0)
        self.assertEqual(hevc_nvenc.surfaces, 0)
        h264_nvenc.surfaces = 1
        hevc_nvenc.surfaces = 1
        self.assertEqual(h264_nvenc.surfaces, 1)
        self.assertEqual(hevc_nvenc.surfaces, 1)
        h264_nvenc.surfaces = 8
        hevc_nvenc.surfaces = 8
        self.assertEqual(h264_nvenc.surfaces, 8)
        self.assertEqual(hevc_nvenc.surfaces, 8)
        h264_nvenc.surfaces = 16
        hevc_nvenc.surfaces = 16
        self.assertEqual(h264_nvenc.surfaces, 16)
        self.assertEqual(hevc_nvenc.surfaces, 16)
        h264_nvenc.surfaces = 512
        hevc_nvenc.surfaces = 512
        self.assertEqual(h264_nvenc.surfaces, 512)
        self.assertEqual(hevc_nvenc.surfaces, 512)

    def _test_surfaces_abnormal_values(self, h264_nvenc, hevc_nvenc):
        # Invalid values that shouldn't apply.
        h264_nvenc.surfaces = -1
        hevc_nvenc.surfaces = -1
        self.assertEqual(h264_nvenc.surfaces, 8)
        self.assertEqual(hevc_nvenc.surfaces, 8)
        h264_nvenc.surfaces = -512
        hevc_nvenc.surfaces = -512
        self.assertEqual(h264_nvenc.surfaces, 8)
        self.assertEqual(hevc_nvenc.surfaces, 8)
        h264_nvenc.surfaces = None
        hevc_nvenc.surfaces = None
        self.assertEqual(h264_nvenc.surfaces, 8)
        self.assertEqual(hevc_nvenc.surfaces, 8)


if __name__ == '__main__':
    unittest.main()
