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

from render_watch.ffmpeg.aac import Aac


class TestAACBitrate(unittest.TestCase):
    """Tests all Bitrate option values of the AAC object."""

    def test_bitrate(self):
        """Tests the Bitrate option of the AAC object."""
        aac = Aac()
        self._test_bitrate_normal_values(aac)
        self._test_bitrate_normal_values(aac)

    def _test_bitrate_normal_values(self, aac):
        # Values that should apply.
        aac.bitrate = 512
        self.assertEqual(aac.bitrate, 512)
        aac.bitrate = 256
        self.assertEqual(aac.bitrate, 256)
        aac.bitrate = 335
        self.assertEqual(aac.bitrate, 335)

    def _test_bitrate_abnormal_values(self, aac):
        # Invalid values that shouldn't apply.
        aac.bitrate = 0
        self.assertEqual(aac.bitrate, 128)
        aac.bitrate = 1024
        self.assertEqual(aac.bitrate, 128)
        aac.bitrate = -1
        self.assertEqual(aac.bitrate, 128)
        aac.bitrate = -1024
        self.assertEqual(aac.bitrate, 128)
        aac.bitrate = None
        self.assertEqual(aac.bitrate, 128)


if __name__ == '__main__':
    unittest.main()
