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


class TestX265NoHighTier(unittest.TestCase):
    """Tests all No High Tier option values for the x265 codec."""

    def test_x265_no_high_tier(self):
        """Tests the No High Tier option values for the x265 codec."""
        x265 = X265()
        self._test_no_high_tier_normal_values(x265)
        self._test_no_high_tier_abormal_values(x265)

    def _test_no_high_tier_normal_values(self, x265):
        # Values that sould apply.
        x265.no_high_tier = True
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = False
        self.assertFalse(x265.no_high_tier)

    def _test_no_high_tier_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.no_high_tier = 1
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = 10
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = -1
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = -10
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = 'Hello, World!'
        self.assertTrue(x265.no_high_tier)
        x265.no_high_tier = 0
        self.assertFalse(x265.no_high_tier)
        x265.no_high_tier = None
        self.assertFalse(x265.no_high_tier)
        x265.no_high_tier = ''
        self.assertFalse(x265.no_high_tier)


if __name__ == '__main__':
    unittest.main()
