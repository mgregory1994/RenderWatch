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


class TestVP9Bitrate(unittest.TestCase):
    """Tests all Bitrate option values for the VP9 object."""

    def test_bitrate(self):
        """Tests Bitrate option values of VP9 object."""
        vp9 = VP9()
        self._test_bitrate_normal_values(vp9)
        self._test_bitrate_abnormal_values(vp9)

    def _test_bitrate_normal_values(self, vp9):
        # Values that should apply.
        vp9.bitrate = 0
        self.assertEqual(vp9.bitrate, 0)
        vp9.bitrate = 1
        self.assertEqual(vp9.bitrate, 1)
        vp9.bitrate = 320
        self.assertEqual(vp9.bitrate, 320)
        vp9.bitrate = 2500
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = 11100
        self.assertEqual(vp9.bitrate, 11100)
        vp9.bitrate = 99999
        self.assertEqual(vp9.bitrate, 99999)

    def _test_bitrate_abnormal_values(self, vp9):
        # Invalid values that shouldn't apply.
        vp9.bitrate = -1
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = -2500
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = -99999
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = -100000
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = 100000
        self.assertEqual(vp9.bitrate, 2500)
        vp9.bitrate = None
        self.assertEqual(vp9.bitrate, 2500)


if __name__ == '__main__':
    unittest.main()
