import unittest

from render_watch.ffmpeg.aac import Aac


class TestAAC(unittest.TestCase):
    def test_instantiation(self):
        aac = Aac()
        self.assertEqual(aac.bitrate, 128)
        self.assertEqual(aac.channels, 0)

    def test_bitrate(self):
        aac = Aac()
        self._test_bitrate_normal_values(aac)
        self._test_bitrate_normal_values(aac)

    def _test_bitrate_normal_values(self, aac):
        aac.bitrate = 512
        self.assertEqual(aac.bitrate, 512)
        aac.bitrate = 256
        self.assertEqual(aac.bitrate, 256)
        aac.bitrate = 335
        self.assertEqual(aac.bitrate, 335)

    def _test_bitrate_abnormal_values(self, aac):
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

    def test_channels(self):
        aac = Aac()
        self._test_channels_normal_values(aac)
        self._test_channels_abnormal_values(aac)

    def _test_channels_normal_values(self, aac):
        aac.channels = 0
        self.assertEqual(aac.channels, 0)
        aac.channels = 1
        self.assertEqual(aac.channels, 1)
        aac.channels = 2
        self.assertEqual(aac.channels, 2)
        aac.channels = 3
        self.assertEqual(aac.channels, 3)
        aac.channels = 4
        self.assertEqual(aac.channels, 4)
        aac.channels = 5
        self.assertEqual(aac.channels, 5)
        aac.channels = 6
        self.assertEqual(aac.channels, 6)

    def _test_channels_abnormal_values(self, aac):
        aac.channels = -1
        self.assertEqual(aac.channels, 0)
        aac.channels = -10
        self.assertEqual(aac.channels, 0)
        aac.channels = 10
        self.assertEqual(aac.channels, 0)
        aac.channels = None
        self.assertEqual(aac.channels, 0)


if __name__ == '__main__':
    unittest.main()
