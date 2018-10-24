#! /usr/bin/python3

# processes 1 daily Pxx archive
# and make an diagram image
# f(freq, t)

import sys
from os import path, listdir
import numpy as np
# import matplotlib
# matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
# import librosa
from astral import Astral, Location
from datetime import date

station = 'INB - Inter'
station_state = 'Resende'
timezone = "Etc/UTC"
stations = {'INB - Inter': ('Pod Inter', -44.654804, -22.519284, -146.8,
                            69.78)}


def get_gain(sens, conv_factor):
    """ calculate gain
    sens = [dB] sensibility hydrophone + conditioner
    conv_factor = [dB] factor for conversion volt -> wav_units oceanPod
    """
    sens_dB = - (-20*np.log10(20e-6) + sens)
    k1 = 10**(sens_dB/20)
    k2 = 10**(conv_factor/20)
    return k2/k1


def get_y_m_d(fpathname):
    fname = fpathname.split('/')[-1]
    fname_short = fname.split('.')[0]
    pxx_str, year_str, month_str, day_str = fname_short.split('_')
    return int(year_str), int(month_str), int(day_str)


if __name__ == '__main__':
    """ reads one archive (24h)
    """

    if len(sys.argv) < 2:
        print("usage: {} <24h pxx file>".format(sys.argv[0]))
        # print(f"usage: {sys.argv[0]} <24h pxx file> <max value file>")
        sys.exit(1)

    fname = sys.argv[1]
    # fname_maxval = sys.argv[2]
    # maxval = np.loadtxt(fname_maxval, dtype=np.float32)

    # [dB] sensibility hydrophone + conditioner
    sens = stations[station][3]
    # [dB] factor for conversion volt -> wav_units oceanPod
    conv_factor = stations[station][4]

    loc = Location(info=(station, station_state, stations[station][2],
                         stations[station][1], timezone, 100))

    pxx = np.loadtxt(fname, dtype=np.float32)
    # print("archive loaded")
    pxx_reduced = np.zeros((1000, 1440))
    count = 0
    # spectrum is 16001 x 1440
    # reduce 16001 -> 1200
    for row in pxx.T:
        # discard DC freq
        spec_line = row.copy()[1:]
        # decrement num of freq
        # sum up 12 values for each new spectrum
        pxx_reduced[:, count] = spec_line.reshape(1000, 16).mean(axis=1)
        count += 1

    # print('reduce done')
    # pxx_flipped = np.flip(pxx_reduced, 0)
    # pxx_gained = pxx_reduced * ( 2 ** get_gain(sens, conv_factor))
    pxx_gained = pxx_reduced * (2 ** 1)

    pxx_dB = 20 * np.log10(pxx_gained/20e-6)

    fig, ax = plt.subplots()
    im = ax.imshow(pxx_dB, origin='lower', cmap='jet', interpolation="none")
    plt.colorbar(im)
    # ax.colorbar()

    num_hours = 24
    ax.set_xticks([h*60 for h in range(num_hours)])
    ax.set_xticklabels([hl for hl in range(num_hours)])

    ax.set_yticks([f*100*10/16 for f in range(16+1)])
    ax.set_yticklabels([fl for fl in range(16+1)])

    ax.set_ylabel("Frequency [kHz]")
    ax.set_xlabel("Daytime [h in UTC]")

    y, m, d = get_y_m_d(fname)
    imagedate = date(y, m, d)
    sun = loc.sun(local=True, date=imagedate)

    sunrise = sun['sunrise']
    ax.vlines(sunrise.hour*60+sunrise.minute, 1, 999, colors='gold',
              linestyles='dashed', label='sunrise', linewidth=1)

    sunset = sun['sunset']
    ax.vlines(sunset.hour*60+sunset.minute, 1, 999, colors='gold',
              linestyles='dashed', label='sunrise', linewidth=1)
    A = Astral()
    moonphase = A.moon_phase(imagedate)
    if moonphase <= 3.5:
        moon_str = 'new moon'
    elif moonphase <= 10.5:
        moon_str = 'first quarter'
    elif moonphase <= 17.5:
        moon_str = 'full moon'
    else:
        moon_str = 'last quarter'

    image_title = (station + ' ' + imagedate.strftime('%d %b %Y') +
                   ' Moon Phase: ' + moon_str)
    ax.set_title(image_title)
    fig.savefig(station + '_' + imagedate.strftime('%d_%b_%Y') + '.png')

    # plt.show()

    # melogram = librosa.feature.melspectrogram(S=pxx, n_fft=12000)
    # fig2, ax2 = plt.subplots()
    # im = ax2.imshow(melogram)
    # plt.show()
