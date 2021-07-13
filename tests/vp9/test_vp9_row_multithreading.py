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


class TestVP9RowMultithreading(unittest.TestCase):
    """Tests all Row Multithreading option values for the VP9 object."""

    def test_row_multithreading(self):
        """Tests Row Multithreading option values for VP9 object."""
        vp9 = VP9()
        self._test_row_multithreading_normal_values(vp9)
        self._test_row_multithreading_abnormal_values(vp9)

    def _test_row_multithreading_normal_values(self, vp9):
        # Values that should apply.
        vp9.row_multithreading = True
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = False
        self.assertFalse(vp9.row_multithreading)

    def _test_row_multithreading_abnormal_values(self, vp9):
        # Invalid values that shouldn't apply.
        vp9.row_multithreading = 1
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = 10
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = -1
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = -10
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = 'Hello, world!'
        self.assertTrue(vp9.row_multithreading)
        vp9.row_multithreading = 0
        self.assertFalse(vp9.row_multithreading)
        vp9.row_multithreading = None
        self.assertFalse(vp9.row_multithreading)
        vp9.row_multithreading = ''
        self.assertFalse(vp9.row_multithreading)


if __name__ == '__main__':
    unittest.main()
