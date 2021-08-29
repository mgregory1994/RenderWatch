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


class TestX264PsyRD(unittest.TestCase):
    """Tests all PsyRD option values for the x264 codec."""

    def test_psy_rd(self):
        """Tests the PsyRD option values for the x264 codec."""
        x264 = X264()
        self._test_psy_rd_normal_values(x264)
        self._test_psy_rd_abnormal_values(x264)

    def _test_psy_rd_normal_values(self, x264):
        # Values that should apply.
        x264.psy_rd = 1.0, 0.0
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))
        x264.psy_rd = 1.1, 0.1
        self.assertTupleEqual(x264.psy_rd, (1.1, 0.1))
        x264.psy_rd = 2.5, 1.25
        self.assertTupleEqual(x264.psy_rd, (2.5, 1.25))
        x264.psy_rd = 0.1, 0.25
        self.assertTupleEqual(x264.psy_rd, (0.1, 0.25))
        x264.psy_rd = 0.0, 0.0
        self.assertTupleEqual(x264.psy_rd, (0.0, 0.0))

    def _test_psy_rd_abnormal_values(self, x264):
        # Values that shouldn't apply.
        x264.psy_rd = -1.0, 0.0
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))
        x264.psy_rd = 0.0, -1.0
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))
        x264.psy_rd = -1.0, -1.0
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))
        x264.psy_rd = None
        self.assertTupleEqual(x264.psy_rd, (1.0, 0.0))


if __name__ == '__main__':
    unittest.main()
