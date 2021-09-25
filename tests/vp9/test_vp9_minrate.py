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


class TestVP9Minrate(unittest.TestCase):
    """Tests all Minrate option values for the VP9 object."""

    def test_minrate(self):
        """Tests Minrate option values for VP9 object."""
        vp9 = VP9()
        self._test_minrate_normal_values(vp9)
        self._test_minrate_abnormal_values(vp9)

    def _test_minrate_normal_values(self, vp9):
        # Values that should apply.
        vp9.minrate = 0
        self.assertEqual(vp9.minrate, 0)
        vp9.minrate = 1
        self.assertEqual(vp9.minrate, 1)
        vp9.minrate = 2500
        self.assertEqual(vp9.minrate, 2500)
        vp9.minrate = 99999
        self.assertEqual(vp9.minrate, 99999)

    def _test_minrate_abnormal_values(self, vp9):
        # Invalid values that shouldn't apply.
        vp9.minrate = -1
        self.assertIsNone(vp9.minrate)
        vp9.minrate = -2500
        self.assertIsNone(vp9.minrate)
        vp9.minrate = -99999
        self.assertIsNone(vp9.minrate)
        vp9.minrate = -100000
        self.assertIsNone(vp9.minrate)
        vp9.minrate = 100000
        self.assertIsNone(vp9.minrate)
        vp9.minrate = None
        self.assertIsNone(vp9.minrate)


if __name__ == '__main__':
    unittest.main()
