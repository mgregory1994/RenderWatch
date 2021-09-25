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


class TestX265SubME(unittest.TestCase):
    """Tests all Sub-Motion Estimation option values for the x265 codec."""

    def test_x265_subme(self):
        """Tests the Sub-Motion Estimation option values for the x265 codec."""
        x265 = X265()
        self._test_subme_normal_values(x265)
        self._test_subme_abnormal_values(x265)

    def _test_subme_normal_values(self, x265):
        # Values that should apply.
        x265.subme = 2
        self.assertEqual(x265.subme, 2)
        x265.subme = 100
        self.assertEqual(x265.subme, 100)
        x265.subme = 0
        self.assertEqual(x265.subme, 0)

    def _test_subme_abnormal_values(self, x265):
        # Values that shouldn't apply.
        x265.subme = -1
        self.assertEqual(x265.subme, 2)
        x265.subme = -100
        self.assertEqual(x265.subme, 2)
        x265.subme = None
        self.assertEqual(x265.subme, 2)


if __name__ == '__main__':
    unittest.main()
