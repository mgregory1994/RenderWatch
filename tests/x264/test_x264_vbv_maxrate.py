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


class TestX264VBVMaxrate(unittest.TestCase):
    """Tests all VBV Maxrate option values for the x264 codec."""

    def test_vbv_maxrate(self):
        """Tests the VBV Maxrate option values for the x264 codec."""
        x264 = X264()
        self._test_vbv_maxrate_normal_values(x264)
        self._test_vbv_maxrate_abnormal_values(x264)

    def _test_vbv_maxrate_normal_values(self, x264):
        # Values that should apply.
        x264.vbv_maxrate = 0
        self.assertEqual(x264.vbv_maxrate, 0)
        x264.vbv_maxrate = 1
        self.assertEqual(x264.vbv_maxrate, 1)
        x264.vbv_maxrate = 2500
        self.assertEqual(x264.vbv_maxrate, 2500)
        x264.vbv_maxrate = 50000
        self.assertEqual(x264.vbv_maxrate, 50000)
        x264.vbv_maxrate = 99999
        self.assertEqual(x264.vbv_maxrate, 99999)

    def _test_vbv_maxrate_abnormal_values(self, x264):
        # Invalid values that shouldn't apply.
        x264.vbv_maxrate = -1
        self.assertEqual(x264.vbv_maxrate, 2500)
        x264.vbv_maxrate = -50000
        self.assertEqual(x264.vbv_maxrate, 2500)
        x264.vbv_maxrate = -100000
        self.assertEqual(x264.vbv_maxrate, 2500)
        x264.vbv_maxrate = 100000
        self.assertEqual(x264.vbv_maxrate, 2500)
        x264.vbv_maxrate = None
        self.assertEqual(x264.vbv_maxrate, 2500)


if __name__ == '__main__':
    unittest.main()
