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


class TestX265EncodePass(unittest.TestCase):
    """Tests all Encode Pass option values for the X265 codec."""

    def test_x265_encode_pass(self):
        """Tests the Encode Pass option values for the x265 codec."""
        x265 = X265()
        self._test_encode_pass_normal_values(x265)
        self._test_encode_pass_abnormal_values(x265)

    def _test_encode_pass_normal_values(self, x265):
        # Values that should apply.
        x265.encode_pass = 1
        self.assertEqual(x265.encode_pass, 1)
        x265.encode_pass = 2
        self.assertEqual(x265.encode_pass, 2)

    def _test_encode_pass_abnormal_values(self, x265):
        # Values that shouldn't apply.
        x265.encode_pass = -1
        self.assertIsNone(x265.encode_pass)
        x265.encode_pass = -100000
        self.assertIsNone(x265.encode_pass)
        x265.encode_pass = 0
        self.assertIsNone(x265.encode_pass)
        x265.encode_pass = 3
        self.assertIsNone(x265.encode_pass)
        x265.encode_pass = None
        self.assertIsNone(x265.encode_pass)


if __name__ == '__main__':
    unittest.main()
