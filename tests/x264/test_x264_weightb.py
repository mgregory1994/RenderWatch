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


class TestX264WeightB(unittest.TestCase):
    """Tests all Weight-B option values for the x264 codec."""

    def test_weightb(self):
        """Tests the Weight-B option values for the x264 codec."""
        x264 = X264()
        self._test_weightb_normal_values(x264)
        self._test_weightb_abnormal_values(x264)

    def _test_weightb_normal_values(self, x264):
        # Values that should apply.
        x264.weightb = True
        self.assertTrue(x264.weightb)
        x264.weightb = False
        self.assertFalse(x264.weightb)

    def _test_weightb_abnormal_values(self, x264):
        # Invalid values that shouldn't apply.
        x264.weightb = 1
        self.assertTrue(x264.weightb)
        x264.weightb = 10
        self.assertTrue(x264.weightb)
        x264.weightb = -1
        self.assertTrue(x264.weightb)
        x264.weightb = -10
        self.assertTrue(x264.weightb)
        x264.weightb = 'Hello, world!'
        self.assertTrue(x264.weightb)
        x264.weightb = 0
        self.assertFalse(x264.weightb)
        x264.weightb = None
        self.assertFalse(x264.weightb)
        x264.weightb = ''
        self.assertFalse(x264.weightb)


if __name__ == '__main__':
    unittest.main()
