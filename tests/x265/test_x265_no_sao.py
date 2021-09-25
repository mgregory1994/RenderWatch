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


class TestX265NoSAO(unittest.TestCase):
    """Tests all No SAO option values for the x265 codec."""

    def test_x265_no_sao(self):
        """Tests the No SAO option values for the x265 codec."""
        x265 = X265()
        self._test_no_sao_normal_values(x265)
        self._test_no_sao_abormal_values(x265)

    def _test_no_sao_normal_values(self, x265):
        # Values that sould apply.
        x265.no_sao = True
        self.assertTrue(x265.no_sao)
        x265.no_sao = False
        self.assertFalse(x265.no_sao)

    def _test_no_sao_abormal_values(self, x265):
        # Values that shouldn't apply.
        x265.no_sao = 1
        self.assertTrue(x265.no_sao)
        x265.no_sao = 10
        self.assertTrue(x265.no_sao)
        x265.no_sao = -1
        self.assertTrue(x265.no_sao)
        x265.no_sao = -10
        self.assertTrue(x265.no_sao)
        x265.no_sao = 'Hello, World!'
        self.assertTrue(x265.no_sao)
        x265.no_sao = 0
        self.assertFalse(x265.no_sao)
        x265.no_sao = None
        self.assertFalse(x265.no_sao)
        x265.no_sao = ''
        self.assertFalse(x265.no_sao)


if __name__ == '__main__':
    unittest.main()
