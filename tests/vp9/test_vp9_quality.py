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

from render_watch.ffmpeg.vp9 import VP9


class TestVP9Quality(unittest.TestCase):
    """Tests all Quality option values for the VP9 object."""

    def test_quality(self):
        """Test Quality option values of VP9 object."""
        vp9 = VP9()
        self._test_quality_normal_values(vp9)
        self._test_quality_abnormal_values(vp9)

    def _test_quality_normal_values(self, vp9):
        # Values that should apply.
        vp9.quality = 0
        self.assertEqual(vp9.quality, 0)
        vp9.quality = 1
        self.assertEqual(vp9.quality, 1)
        vp9.quality = 2
        self.assertEqual(vp9.quality, 2)
        vp9.quality = 3
        self.assertEqual(vp9.quality, 3)

    def _test_quality_abnormal_values(self, vp9):
        # Invalid values that shouldn't apply.
        vp9.quality = -1
        self.assertEqual(vp9.quality, 0)
        vp9.quality = -10
        self.assertEqual(vp9.quality, 0)
        vp9.quality = 4
        self.assertEqual(vp9.quality, 0)
        vp9.quality = 10
        self.assertEqual(vp9.quality, 0)
        vp9.quality = None
        self.assertEqual(vp9.quality, 0)


if __name__ == '__main__':
    unittest.main()
