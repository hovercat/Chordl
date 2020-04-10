import os
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import scipy.signal as sps
import matplotlib.pyplot as plt
import soundfile as sf  # https://pysoundfile.readthedocs.io/en/latest/
import pandas as pd


def synchronize_multiple(sync, in_dir, out_dir, out_format="flac", threads=22, duration=10, resample_rate=48000,
                         error_resample_div=10):
    """ synchronize all files in in_dir and write to out_dir """

    arguments = [
        (sync,
         os.path.join(in_dir, x),
         os.path.join(out_dir, "{file}.{ext}".format(
             file=os.path.splitext(os.path.basename(x))[0],
             ext=out_format
         )),
         duration,
         resample_rate,
         error_resample_div)
        for x in os.listdir(in_dir)
    ]

    converted_dict = dict()
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = executor.map(_synchronize_helper, arguments)
        executor.shutdown(wait=True)

        for result in futures:
            converted_dict[result[0]] = result[1:]

    error_stats = pd.DataFrame.from_dict(converted_dict, orient="index")
    error_stats.columns=["error_in", "delay", "out_file", "error_out"]
    error_stats.to_csv(os.path.join(out_dir, "sync_stats.csv"))
    return error_stats


def _synchronize_helper(args):
    return synchronize(args[0], args[1], args[2], args[3], args[4], args[5])


def synchronize(file1, file2, out, duration=10, resample_rate=48000, error_resample_div=10):
    """ synchronize file2 to file1 and write to out2 """

    error_frames, delay, error = get_error(file1, file2, duration, resample_rate, error_resample_div)

    with sf.SoundFile(file2, 'r') as sfile2:
        data = sfile2.read()
        data_res = sps.resample(data, int((data.shape[0] / sfile2.samplerate) * resample_rate))

        data_sync = data_res
        if error_frames < 0:
            silence = np.zeros((error_frames, 2))
            data_sync = np.concatenate((silence, data_res))
        else:
            data_sync = data_res[error_frames:, :]

        sf.write(out, data_sync, resample_rate)

    res_error_frames, res_delay, res_error = get_error(file1, out, duration, resample_rate, error_resample_div)

    return file2, error, delay, out, res_error


def get_error(file1, file2, duration=10, resample_rate=48000, error_resample_div=10):
    """ get time delay of signal """

    with sf.SoundFile(file1, 'r') as sfile1, sf.SoundFile(file2, 'r') as sfile2:
        signal1 = sps.resample(sfile1.read(duration * sfile1.samplerate), duration * resample_rate)
        signal2 = sps.resample(sfile2.read(duration * sfile2.samplerate), duration * resample_rate)

        # one channel only
        signal1 = signal1[:, 0]  # take left channel only
        signal2 = signal2[:, 0]  # take left channel only
        assert (signal1.shape == signal2.shape)

        # normalize
        normalized1 = signal1 / np.max(np.abs(signal1))
        normalized2 = signal2 / np.max(np.abs(signal2))

        acceleration1 = np.gradient(np.gradient(normalized1))
        acceleration2 = np.gradient(np.gradient(normalized2))

        acc1_res_abs = np.abs(sps.resample(acceleration1, int(len(acceleration1) / error_resample_div)))
        acc2_res_abs = np.abs(sps.resample(acceleration2, int(len(acceleration2) / error_resample_div)))

        error_pos1, error1 = _shift_signals(acc1_res_abs, acc2_res_abs, shift_width=10)
        error_pos2, error2 = _shift_signals(acc2_res_abs, acc1_res_abs, shift_width=10)

        if error1 < error2:
            error = error1
            error_pos = error_pos1 * error_resample_div
        else:
            error = error2
            error_pos = error_pos2 * error_resample_div

        print("Error: {}, Position: {}".format(
            error,
            error_pos / resample_rate
        ))

        return error_pos, error_pos / resample_rate, error
        # return error_pos / resample_rate, error


def _shift_signals(signal1, signal2, shift_width):
    min_error = 1
    min_error_position = 0
    l = signal1.shape[0]
    for i in range(0, l, shift_width):
        error_overlap = np.sum(np.abs(signal1[i:l] - signal2[0:l - i]))
        error_rest1 = np.sum(signal1[0:i])
        error_rest2 = np.sum(signal2[l - i:l])
        error = np.square((error_overlap + error_rest1 + error_rest2) / l)
        if error < min_error:
            min_error = error
            min_error_position = i

    return min_error_position, min_error


def _plot_signals(signal1, signal2):
    plt.plot(signal1)
    plt.plot(signal2)

    plt.show()
