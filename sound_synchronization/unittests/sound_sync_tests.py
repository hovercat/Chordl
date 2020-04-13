import os
import unittest

from sound_synchronization.sound_synchronization import get_error, synchronize, synchronize_multiple
import soundfile as sf


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

        synchronize_multiple("resources/sync2.ogg", "resources/in2", "resources/out2", threads=1, out_format="flac")

    def test_multisynchronize_real(self):
        for file in os.listdir("resources/real_example/out/"):
            os.remove(os.path.join("resources/real_example/out", file))

        synchronize_multiple("resources/real_example/Master.ogg", "resources/real_example/in", "resources/real_example/out", threads=4, out_format="flac")

    def test_multisynchronize_real01(self):
        if os.path.exists("resources/real_example/33.flac"):
            os.remove("resources/real_example/33.flac")


        with sf.SoundFile("resources/real_example/Master.ogg", 'r') as sync_file:
            sync_signal = sync_file.read(10 * sync_file.samplerate)
            synchronize(sync_signal, sync_file.samplerate, "resources/real_example/in/33.ogg", "resources/real_example/33.flac", error_resample_div=10)
        self.assertTrue(os.path.exists("resources/real_example/33.flac"))


    def test_multisynchronize_real05(self):
        if os.path.exists("resources/real_example/05.flac"):
            os.remove("resources/real_example/05.flac")

        with sf.SoundFile("resources/real_example/Master.ogg", 'r') as sync_file:
            sync_signal = sync_file.read(10 * sync_file.samplerate)
            synchronize(sync_signal, sync_file.samplerate, "resources/real_example/in/05.ogg", "resources/real_example/05.flac", error_resample_div=10)


if __name__ == '__main__':
    unittest.main()
