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


class TestVP9Speed(unittest.TestCase):
    """Tests all Speed option values for the VP9 object."""

    def test_speed(self):
        """Tests Speed option values of VP9 object."""
        vp9 = VP9()
        self._test_speed_normal_values(vp9)
        self._test_speed_abnormal_values(vp9)

    def _test_speed_normal_values(self, vp9):
        # Values that should apply.
        vp9.speed = 0
        self.assertEqual(vp9.speed, 0)
        vp9.speed = 1
        self.assertEqual(vp9.speed, 1)
        vp9.speed = 2
        self.assertEqual(vp9.speed, 2)
        vp9.speed = 3
        self.assertEqual(vp9.speed, 3)
        vp9.speed = 4
        self.assertEqual(vp9.speed, 4)
        vp9.speed = 5
        self.assertEqual(vp9.speed, 5)
        vp9.speed = 6
        self.assertEqual(vp9.speed, 6)

    def _test_speed_abnormal_values(self, vp9):
        # Invalid values that shouldn't apply.
        vp9.speed = -1
        self.assertEqual(vp9.speed, 0)
        vp9.speed = -10
        self.assertEqual(vp9.speed, 0)
        vp9.speed = 7
        self.assertEqual(vp9.speed, 0)
        vp9.speed = 10
        self.assertEqual(vp9.speed, 0)
        vp9.speed = None
        self.assertEqual(vp9.speed, 0)


if __name__ == '__main__':
    unittest.main()
