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

from render_watch.ffmpeg.hevc_nvenc import HevcNvenc


class TestNvencTier(unittest.TestCase):
    """Tests all Tier option values for the HEVC NVENC codec."""

    def test_tier(self):
        """Tests the Tier option values for the HEVC NVENC codec."""
        hevc_nvenc = HevcNvenc()
        self._test_tier_normal_values(hevc_nvenc)
        self._test_tier_abnormal_values(hevc_nvenc)

    def _test_tier_normal_values(self, hevc_nvenc):
        # Values that should apply.
        hevc_nvenc.tier = True
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = False
        self.assertFalse(hevc_nvenc.tier)

    def _test_tier_abnormal_values(self, hevc_nvenc):
        # Invalid values that shouldn't apply.
        hevc_nvenc.tier = -1
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = -10
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = 0
        self.assertFalse(hevc_nvenc.tier)
        hevc_nvenc.tier = 1
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = 10
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = 'Hello, World!'
        self.assertTrue(hevc_nvenc.tier)
        hevc_nvenc.tier = ''
        self.assertFalse(hevc_nvenc.tier)
        hevc_nvenc.tier = None
        self.assertFalse(hevc_nvenc.tier)


if __name__ == '__main__':
    unittest.main()
