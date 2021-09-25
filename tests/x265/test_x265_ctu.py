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


class TestX265CTU(unittest.TestCase):
    """Tests all CTU option values for the x265 codec."""

    def test_x265_ctu(self):
        """Tests the CTU option values for the x265 codec."""
        x265 = X265()
        self._test_ctu_normal_values(x265)
        self._test_ctu_abnormal_values(x265)

    def _test_ctu_normal_values(self, x265):
        # Values that should apply.
        x265.ctu = 0
        self.assertEqual(x265.ctu, 0)
        x265.ctu = 1
        self.assertEqual(x265.ctu, 1)
        x265.ctu = X265.MAX_CU_SIZE_LIST_LENGTH - 1
        self.assertEqual(x265.ctu, X265.MAX_CU_SIZE_LIST_LENGTH - 1)

    def _test_ctu_abnormal_values(self, x265):
        # Values that shouldn't apply.
        x265.ctu = -1
        self.assertEqual(x265.ctu, 0)
        x265.ctu = X265.MAX_CU_SIZE_LIST_LENGTH * -1
        self.assertEqual(x265.ctu, 0)
        x265.ctu = X265.MAX_CU_SIZE_LIST_LENGTH
        self.assertEqual(x265.ctu, 0)
        x265.ctu = None
        self.assertEqual(x265.ctu, 0)


if __name__ == '__main__':
    unittest.main()
