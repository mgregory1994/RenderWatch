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


class TestX265AMP(unittest.TestCase):
    """Tests all AMP option values for the x265 codec."""

    def test_x265_amp(self):
        """Tests the AMP option values for the x265 codec."""
        x265 = X265()
        self._test_amp_normal_values(x265)
        self._test_amp_abormal_values(x265)

    def _test_amp_normal_values(self, x265):
        # Values that sould apply.
        x265.amp = True
        self.assertTrue(x265.amp)
        x265.amp = False
        self.assertFalse(x265.amp)

    def _test_amp_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.amp = 1
        self.assertTrue(x265.amp)
        x265.amp = 10
        self.assertTrue(x265.amp)
        x265.amp = -1
        self.assertTrue(x265.amp)
        x265.amp = -10
        self.assertTrue(x265.amp)
        x265.amp = 'Hello, World!'
        self.assertTrue(x265.amp)
        x265.amp = 0
        self.assertFalse(x265.amp)
        x265.amp = None
        self.assertFalse(x265.amp)
        x265.amp = ''
        self.assertFalse(x265.amp)


if __name__ == '__main__':
    unittest.main()
