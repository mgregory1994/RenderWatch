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


class TestOpus(unittest.TestCase):
    """Tests all Opus options."""

    def test_instantiation(self):
        """Tests the initial values of Opus object."""
        opus = Opus()
        self.assertEqual(opus.bitrate, 128)
        self.assertEqual(opus.channels, 0)

    def test_bitrate(self):
        """Test Bitrate values of Opus object."""
        opus = Opus()
        self._test_bitrate_normal_values(opus)
        self._test_bitrate_abnormal_values(opus)

    def _test_bitrate_normal_values(self, opus):
        # Values that should apply.
        opus.bitrate = 128
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = 256
        self.assertEqual(opus.bitrate, 256)
        opus.bitrate = 320
        self.assertEqual(opus.bitrate, 320)
        opus.bitrate = 512
        self.assertEqual(opus.bitrate, 512)
        opus.bitrate = 444
        self.assertEqual(opus.bitrate, 444)

    def _test_bitrate_abnormal_values(self, opus):
        # Invalid values that shouldn't apply.
        opus.bitrate = 0
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -1
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = -1024
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = 1024
        self.assertEqual(opus.bitrate, 128)
        opus.bitrate = None
        self.assertEqual(opus.bitrate, 128)

    def test_channels(self):
        """Test Channel values of Opus object."""
        opus = Opus()
        self._test_channels_normal_values(opus)
        self._test_channels_abnormal_values(opus)

    def _test_channels_normal_values(self, opus):
        # Values that should apply.
        opus.channels = 0
        self.assertEqual(opus.channels, 0)
        opus.channels = 1
        self.assertEqual(opus.channels, 1)
        opus.channels = 2
        self.assertEqual(opus.channels, 2)
        opus.channels = 3
        self.assertEqual(opus.channels, 3)
        opus.channels = 4
        self.assertEqual(opus.channels, 4)
        opus.channels = 5
        self.assertEqual(opus.channels, 5)
        opus.channels = 6
        self.assertEqual(opus.channels, 6)

    def _test_channels_abnormal_values(self, opus):
        # Invalid values that shouldn't apply.
        opus.channels = -1
        self.assertEqual(opus.channels, 0)
        opus.channels = -10
        self.assertEqual(opus.channels, 0)
        opus.channels = 7
        self.assertEqual(opus.channels, 0)
        opus.channels = 10
        self.assertEqual(opus.channels, 0)
        opus.channels = None
        self.assertEqual(opus.channels, 0)


if __name__ == '__main__':
    unittest.main()
