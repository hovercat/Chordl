
def _shift_signals(signal1, signal2, shift_width):
    """  """

    min_error = 1
    min_error_index = 0
    l = signal1.shape[0]

    signal1 = np.abs(signal1)
    signal2 = np.abs(signal2)

    for i in range(0, l, shift_width):
        error_overlap = np.sum(np.abs(signal1[0:i] - signal2[l - i:l]))
        error_rest1 = np.sum(signal1[i:l])
        error_rest2 = np.sum(signal2[0:l - i])
        error = np.square((error_overlap + error_rest1 + error_rest2) / (l + i))

        if error < min_error:
            min_error = error
            min_error_index = i

    min_error_position = l - min_error_index

    return min_error_position, min_error

def _shift_signals2(master, input, shift_width):
    """ """

    min_error = 1
    min_error_index = 0

    start = master.shape[0]
    if (len(input.shape) == 2):
        end = input.shape[0]
    else:
        end = len(input) # only one channel

    for i in range(-start+1, end-start, shift_width):
        if i < 0:
            s1 = master[-(start+i):]
            s2 = input[:(start+i)]
            error = np.sum(np.abs(s1 - s2)) + np.sum(master[:i*(-1)+1])
            error = error / master.shape[0]

            if error < min_error:
                min_error = error
                min_error_index = i
        else:
            s1 = master
            s2 = input[i:i+(master.shape[0])]
            error = np.sum(np.abs(s1 - s2))
            error = error / master.shape[0]

            if error < min_error:
                min_error = error
                min_error_index = i

    return min_error_index, min_error

def _preprocess_signals(signal1, signal1_samplerate, signal2, signal2_samplerate, resample_rate,
                        error_resample_div):  # todo resampling of e.g 44.1khz
   # p_sign1 = sps.resample(signal1, int(signal1.shape[0] * (resample_rate / signal1_samplerate) / error_resample_div),
   #                        axis=0)
    #p_sign2 = sps.resample(signal2, int(signal2.shape[0] * (resample_rate / signal2_samplerate) / error_resample_div),
    #                       axis=0)
    p_sign1 = signal1
    p_sign2 = signal2

    # if p_sign1.shape[0] > p_sign2.shape[0]:
    #     p_sign2 = np.concatenate((p_sign2, np.zeros((p_sign1.shape[0] - p_sign2.shape[0], 2))))
    # #if p_sign1.shape[0] < p_sign2.shape[0]:
    # #    p_sign1 = np.concatenate((p_sign1, np.zeros((p_sign2.shape[0] - p_sign1.shape[0], 2))))
    #
    # p_sign1 = np.gradient(np.gradient(p_sign1, axis=0), axis=0)
    # p_sign2 = np.gradient(np.gradient(p_sign2, axis=0), axis=0)
    #
    # B, A = sps.butter(4, 1/50, output='ba')
    # p_sign1 = sps.filtfilt(B, A, np.abs(p_sign1), axis=0)
    # p_sign2 = sps.filtfilt(B, A, np.abs(p_sign2), axis=0)

    #p_sign1 = sps.resample(p_sign1, int(p_sign1.shape[0] * (resample_rate / signal1_samplerate) / error_resample_div),
    #                       axis=0)

    if signal2_samplerate != signal1_samplerate:
        p_sign2 = sps.resample(p_sign2, p_sign1.shape[0] * signal1_samplerate, axis=0)


    # p_sign1 = skp.maxabs_scale(p_sign1)
    # p_sign2 = skp.maxabs_scale(p_sign2)
    #
    # p_sign1 = sps.medfilt2d(p_sign1, 3)
    # p_sign2 = sps.medfilt2d(p_sign2, 3)
    #
    # p_sign1 = skp.maxabs_scale(p_sign1)
    # p_sign2 = skp.maxabs_scale(p_sign2)
    #
    # p_sign1[p_sign1 < 0] = 0
    # p_sign2[p_sign2 < 0] = 0

    return p_sign1, p_sign2