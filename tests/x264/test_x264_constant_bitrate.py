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

from render_watch.ffmpeg.x264 import X264


class TestX264ConstantBitrate(unittest.TestCase):
    """Tests all Constant Bitrate option values for the x264 codec."""

    def test_constant_bitrate(self):
        """Tests the Constant Bitrate option values for the x264 codec."""
        x264 = X264()
        self._test_constant_bitrate_normal_values(x264)
        self._test_constant_bitrate_abnormal_values(x264)

    def _test_constant_bitrate_normal_values(self, x264):
        # Values that should apply.
        x264.constant_bitrate = True
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = False
        self.assertFalse(x264.constant_bitrate)

    def _test_constant_bitrate_abnormal_values(self, x264):
        # Invalid values that shouldn't apply.
        x264.constant_bitrate = 1
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = 10
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = -1
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = -10
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = 'Hello, world!'
        self.assertTrue(x264.constant_bitrate)
        x264.constant_bitrate = 0
        self.assertFalse(x264.constant_bitrate)
        x264.constant_bitrate = None
        self.assertFalse(x264.constant_bitrate)
        x264.constant_bitrate = ''
        self.assertFalse(x264.constant_bitrate)


if __name__ == '__main__':
    unittest.main()
