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


class TestX265RCLookahead(unittest.TestCase):
    """Tests all RC-Lookahead option values for the X265 codec."""

    def test_x265_rc_lookahead(self):
        """Tests the RC-Lookahead option values for the x265 codec."""
        x265 = X265()
        self._test_rc_lookahead_normal_values(x265)
        self._test_rc_lookahead_abnormal_values(x265)

    def _test_rc_lookahead_normal_values(self, x265):
        # Values that should apply.
        x265.rc_lookahead = 20
        self.assertEqual(x265.rc_lookahead, 20)
        x265.rc_lookahead = 99999
        self.assertEqual(x265.rc_lookahead, 99999)
        x265.rc_lookahead = 0
        self.assertEqual(x265.rc_lookahead, 0)

    def _test_rc_lookahead_abnormal_values(self, x265):
        # Values that shouldn't apply.
        x265.rc_lookahead = -1
        self.assertEqual(x265.rc_lookahead, 20)
        x265.rc_lookahead = -100000
        self.assertEqual(x265.rc_lookahead, 20)
        x265.rc_lookahead = None
        self.assertEqual(x265.rc_lookahead, 20)


if __name__ == '__main__':
    unittest.main()
