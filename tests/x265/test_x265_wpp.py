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


class TestX265WPP(unittest.TestCase):
    """Tests all WPP option values for the x265 codec."""

    def test_x265_wpp(self):
        """Tests the WPP option values for the x265 codec."""
        x265 = X265()
        self._test_wpp_normal_values(x265)
        self._test_wpp_abormal_values(x265)

    def _test_wpp_normal_values(self, x265):
        # Values that sould apply.
        x265.wpp = True
        self.assertTrue(x265.wpp)
        x265.wpp = False
        self.assertFalse(x265.wpp)

    def _test_wpp_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.wpp = 1
        self.assertTrue(x265.wpp)
        x265.wpp = 10
        self.assertTrue(x265.wpp)
        x265.wpp = -1
        self.assertTrue(x265.wpp)
        x265.wpp = -10
        self.assertTrue(x265.wpp)
        x265.wpp = 'Hello, World!'
        self.assertTrue(x265.wpp)
        x265.wpp = 0
        self.assertFalse(x265.wpp)
        x265.wpp = None
        self.assertFalse(x265.wpp)
        x265.wpp = ''
        self.assertFalse(x265.wpp)


if __name__ == '__main__':
    unittest.main()
