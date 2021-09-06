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

from render_watch.ffmpeg.x265 import X265


class TestX265UHDBD(unittest.TestCase):
    """Tests all UHD BD option values for the x265 codec."""

    def test_x265_uhd_bd(self):
        """Tests the UHD BD option values for the x265 codec."""
        x265 = X265()
        self._test_uhd_bd_normal_values(x265)
        self._test_uhd_bd_abormal_values(x265)

    def _test_uhd_bd_normal_values(self, x265):
        # Values that sould apply.
        x265.uhd_bd = True
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = False
        self.assertFalse(x265.uhd_bd)

    def _test_uhd_bd_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.uhd_bd = 1
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = 10
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = -1
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = -10
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = 'Hello, World!'
        self.assertTrue(x265.uhd_bd)
        x265.uhd_bd = 0
        self.assertFalse(x265.uhd_bd)
        x265.uhd_bd = None
        self.assertFalse(x265.uhd_bd)
        x265.uhd_bd = ''
        self.assertFalse(x265.uhd_bd)


if __name__ == '__main__':
    unittest.main()
