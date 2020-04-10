import os
import unittest

from application.sound_synchronization.sound_synchronization import get_error, synchronize, synchronize_multiple


class MyTestCase(unittest.TestCase):
    def test_get_error(self):
        self.assertAlmostEqual(0.237, get_error("resources/sync1.ogg", "resources/in1.ogg")[1], places=2)  # sync1 in1
       # self.assertAlmostEqual(0.237, get_error("resources/sync2.mp3", "resources/in2.ogg"), places=2)  # sync2 in2
        self.assertAlmostEqual(0.235, get_error("resources/sync3.ogg", "resources/in3.ogg")[1], places=2)  # sync3 in3
        self.assertAlmostEqual(0.00, get_error("resources/sync4.ogg", "resources/in4.ogg")[1], places=2)  # sync3 in3

    def test_synchronize(self):
        if os.path.exists("resources/out/out1.flac"):
            os.remove("resources/out/out1.flac")

        synchronize("resources/sync1.ogg", "resources/in1.ogg", "resources/out/out1.flac")
        self.assertTrue(os.path.exists("resources/out/out1.flac"))
        self.assertAlmostEqual(0, get_error("resources/sync1.ogg", "resources/out/out1.flac")[2], places=2)

    def test_multisynchronize(self):
        for file in os.listdir("resources/out1/"):
            os.remove(os.path.join("resources/out1", file))

        synchronize_multiple("resources/sync1.ogg", "resources/in1", "resources/out1", out_format="flac")

    def test_multisynchronize2(self):
        for file in os.listdir("resources/out2/"):
            os.remove(os.path.join("resources/out2", file))

        synchronize_multiple("resources/sync2.ogg", "resources/in2", "resources/out2", out_format="flac")


if __name__ == '__main__':
    unittest.main()
