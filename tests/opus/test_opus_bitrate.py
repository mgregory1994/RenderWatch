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

from render_watch.ffmpeg.opus import Opus


class TestOpusBitrate(unittest.TestCase):
    """Tests all Bitrate option values for the Opus object."""

    def test_bitrate(self):
        """Test Bitrate values of Opus object."""
        opus = Opus()
        self._test_bitrate_normal_values(opus)
        self._test_bitrate_abnormal_values(opus)

    def _test_bitrate_normal_values(self, opus):
        # Values that should apply.
        opus.bitrate = 64
        self.assertEqual(opus.bitrate, 64)
        opus.bitrate = 128
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = 256
        self.assertEqual(opus.bitrate, 256)
        opus.bitrate = 320
        self.assertEqual(opus.bitrate, 320)
        opus.bitrate = 512
        self.assertEqual(opus.bitrate, 512)
        opus.bitrate = 999
        self.assertEqual(opus.bitrate, 999)

    def _test_bitrate_abnormal_values(self, opus):
        # Invalid values that shouldn't apply.
        opus.bitrate = 0
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -1
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -64
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -999
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -1000
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = 63
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = 1000
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = None
        self.assertEqual(opus.bitrate, 128)


if __name__ == '__main__':
    unittest.main()
