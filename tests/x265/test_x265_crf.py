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


class TestX265CRF(unittest.TestCase):
    """Tests all CRF option values for the X265 codec."""

    def test_x265_crf(self):
        """Tests the CRF option values for the x265 codec."""
        x265 = X265()
        self._test_crf_normal_values(x265)
        self._test_crf_abnormal_values(x265)

    def _test_crf_normal_values(self, x265):
        # Values that should apply.
        x265.crf = 20.0
        self.assertEqual(x265.crf, 20.0)
        x265.crf = 21.0
        self.assertEqual(x265.crf, 21.0)
        x265.crf = 30.25
        self.assertEqual(x265.crf, 30.25)
        x265.crf = 51.0
        self.assertEqual(x265.crf, 51.0)
        x265.crf = 0.0
        self.assertEqual(x265.crf, 0.0)

    def _test_crf_abnormal_values(self, x265):
        # Values that shouldn't apply.
        x265.crf = -1.0
        self.assertIsNone(x265.crf)
        x265.crf = -0.25
        self.assertIsNone(x265.crf)
        x265.crf = -51.5
        self.assertIsNone(x265.crf)
        x265.crf = 51.01
        self.assertIsNone(x265.crf)
        x265.crf = None
        self.assertIsNone(x265.crf)


if __name__ == '__main__':
    unittest.main()
