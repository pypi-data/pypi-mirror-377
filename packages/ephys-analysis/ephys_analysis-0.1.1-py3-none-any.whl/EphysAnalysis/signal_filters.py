import numpy as np
from scipy import signal


def butter(arr, cutoff: float=1.0):
    from scipy import signal
    fre = cutoff
    if fre > 1.0:
        fre = 1.0
    b, a = signal.butter(N=4, Wn=fre, btype='lowpass')
    return signal.filtfilt(b, a, arr)


def moving_average(arr, size: int=3):
    b = np.repeat([1.0 / size], size)  # Create impulse response
    return signal.lfilter(b, 1, arr)  # Filter the signal


def fft(arr, low_fre=None, high_fre=None):
    from scipy.fftpack import rfft, irfft, fftfreq

    n = np.fft.fft(arr).size
    W = fftfreq(n=n)
    arr_fft = rfft(arr)
    if low_fre:
        arr_fft[np.where(W < low_fre)] = 0
    if high_fre:
        arr_fft[np.where(W > high_fre)] = 0
    return irfft(arr_fft)


def fft2d():
    pass


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    x = np.arange(50)
    y1 = np.sin(x)+1
    y2 = np.sin(x * 5)+1
    y3 = np.sin(x/10) +1
    y = y1+y2+y3
    yy = fft(y, low_fre=0.1, high_fre=0.3)
    print(yy.mean())
    # plt.plot(y2)
    plt.plot(y1)
    plt.plot(yy)
    plt.show()




