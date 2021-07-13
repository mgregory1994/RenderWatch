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


class TestOpusChannels(unittest.TestCase):
    """Tests all Channels option values for the Opus object."""

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
        opus.channels = Opus.CHANNELS_LIST_LENGTH - 1
        self.assertEqual(opus.channels, Opus.CHANNELS_LIST_LENGTH - 1)

    def _test_channels_abnormal_values(self, opus):
        # Invalid values that shouldn't apply.
        opus.channels = -1
        self.assertEqual(opus.channels, 0)
        opus.channels = Opus.CHANNELS_LIST_LENGTH * -1
        self.assertEqual(opus.channels, 0)
        opus.channels = 7
        self.assertEqual(opus.channels, 0)
        opus.channels = Opus.CHANNELS_LIST_LENGTH
        self.assertEqual(opus.channels, 0)
        opus.channels = None
        self.assertEqual(opus.channels, 0)


if __name__ == '__main__':
    unittest.main()
