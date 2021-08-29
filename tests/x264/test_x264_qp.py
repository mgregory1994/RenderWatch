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

from render_watch.ffmpeg.x264 import X264


class TestX264QP(unittest.TestCase):
    """Tests all QP option values for the x264 codec."""

    def test_qp(self):
        """Tests the QP option values for the x264 codec."""
        x264 = X264()
        self._test_qp_normal_values(x264)
        self._test_qp_abnormal_values(x264)

    def _test_qp_normal_values(self, x264):
        # Values that should apply.
        x264.qp = 0.0
        self.assertEqual(x264.qp, 0.0)
        x264.qp = 1.0
        self.assertEqual(x264.qp, 1.0)
        x264.qp = 20.5
        self.assertEqual(x264.qp, 20.5)
        x264.qp = 32.75
        self.assertEqual(x264.qp, 32.75)
        x264.qp = 51.0
        self.assertEqual(x264.qp, 51.0)

    def _test_qp_abnormal_values(self, x264):
        # Invalid values that shouldn't apply.
        x264.qp = -1.0
        self.assertIsNone(x264.qp)
        x264.qp = -10.5
        self.assertIsNone(x264.qp)
        x264.qp = -51.1
        self.assertIsNone(x264.qp)
        x264.qp = 51.1
        self.assertIsNone(x264.qp)
        x264.qp = None
        self.assertIsNone(x264.qp)


if __name__ == '__main__':
    unittest.main()
