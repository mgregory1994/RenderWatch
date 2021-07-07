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
    """Tests all Opus initial options."""

    def test_instantiation(self):
        """Tests the initial values of Opus object."""
        opus = Opus()
        self.assertEqual(opus.bitrate, 128)
        self.assertEqual(opus.channels, 0)


if __name__ == '__main__':
    unittest.main()
