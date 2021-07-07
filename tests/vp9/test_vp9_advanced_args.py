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


class TestVP9AdvancedArgs(unittest.TestCase):
    """Tests all Advanced Args option values for the VP9 object."""

    def test_advanced_args(self):
        """Tests Advanced Args option values for VP9 object."""
        vp9 = VP9()
        self.assertIsNone(vp9.get_ffmpeg_advanced_args()[''])


if __name__ == '__main__':
    unittest.main()
