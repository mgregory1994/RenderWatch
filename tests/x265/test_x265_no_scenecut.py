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


class TestX265NoScenecut(unittest.TestCase):
    """Tests all No Scenecut option values for the x265 codec."""

    def test_x265_no_scenecut(self):
        """Tests the No Scenecut option values for the x265 codec."""
        x265 = X265()
        self._test_no_scenecut_normal_values(x265)
        self._test_no_scenecut_abormal_values(x265)

    def _test_no_scenecut_normal_values(self, x265):
        # Values that sould apply.
        x265.no_scenecut = True
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = False
        self.assertFalse(x265.no_scenecut)

    def _test_no_scenecut_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.no_scenecut = 1
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = 10
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = -1
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = -10
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = 'Hello, World!'
        self.assertTrue(x265.no_scenecut)
        x265.no_scenecut = 0
        self.assertFalse(x265.no_scenecut)
        x265.no_scenecut = None
        self.assertFalse(x265.no_scenecut)
        x265.no_scenecut = ''
        self.assertFalse(x265.no_scenecut)


if __name__ == '__main__':
    unittest.main()
