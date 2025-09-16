import numpy as np
import sys
# from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter
import peakutils as pu
from scipy.signal import medfilt
from EphysAnalysis.signal_filters import butter, moving_average, fft
from scipy.signal import peak_widths


class EventSignal:
    def __init__(self, data, rate=5000, positive=True, threshold=3.0):
        """
        :param data: 1-D array like
        :param rate:
        :param threshold: to filter noise and get the events (times of std)
        """

        self.rate = rate
        self.duration_sec = len(data) / self.rate
        # b = np.min(data) if np.min(data) > 0 else 1
        self.data = np.array(data, dtype=np.float64)
        # self.data = self.__filter(np.array(data, dtype=np.float_))
        self.__threshold = threshold
        self.__delta = None  # to filter the events

        self.__baseline = None

        if not positive:
            self.data = - self.data

        # self.__events_total = None
        # self.__min_list = None

        self.__events = None
        self.__num_events = None
        # self.__num_total = 0
        self.__fre = None
        self.__fwhm = None
        self.__rise1090 = None
        self.__decay1090 = None

    def __getitem__(self, item: int):
        return self.data[item]

    def __init(self):
        self.__events = None
        self.__num_events = None
        self.__fre = None
        self.__fwhm = None
    
    @property
    def baseline(self):
        if self.__baseline is None:
            self.__baseline = pu.baseline(self.data)
        return self.__baseline

    @baseline.setter
    def baseline(self, value):
        self.__baseline = value

    @property
    def num_events(self):
        if self.__num_events is None:
            self.get_peaks()
        return self.__num_events

    @property
    def frequency(self):
        if self.__fre is None:
            self.get_peaks()
        return self.__fre

    @property
    def events(self):
        if self.__events is None:
            self.get_peaks()
        return self.__events
    
    @property
    def fwhm(self):
        if self.__fwhm is None:
            self.kinetics()
        return self.__fwhm
    
    @property
    def rise1090(self):
        if self.__rise1090 is None:
            self.kinetics()
        return self.__rise1090
    
    @property
    def decay1090(self):
        if self.__decay1090 is None:
            self.kinetics()
        return self.__decay1090

    @property
    def delta(self):
        if self.__delta is None:
            self.__delta = self.__get_std() * self.__threshold
            # self.__delta = 8
        return self.__delta

    @delta.setter
    def delta(self, value):
        self.__delta = value
        if self.events is not None:
            self.get_peaks()

    def __get_std(self):
        # baseline = self.data - gaussian_filter(self.data, sigma=5)
        return self.data.std()

    @staticmethod
    def __filter(data=None, smooth_filter=2, smooth_pm=5):
        if smooth_filter == 0:
            return butter(data, cutoff=smooth_pm)
        if smooth_filter == 1:
            return moving_average(data, size=smooth_pm)
        if smooth_filter == 2:
            return medfilt(data, int(smooth_pm))
        else:
            return gaussian_filter(data, sigma=smooth_pm)

    @staticmethod
    def __peak_det(v, d, x=None):
        """

        :param v:
        :param d:
        :param x:
        :return: (events amplitudes (x, y), local minimum (x, y))
        """
        maxtab = []
        mintab = []

        if x is None:
            x = np.arange(len(v))

        v = np.asarray(v)

        if len(v) != len(x):
            sys.exit('Input vectors v and x must have same length')

        if not np.isscalar(d):
            sys.exit('Input argument delta must be a scalar')

        if d <= 0:
            sys.exit('Input argument delta must be positive')

        mn, mx = np.inf, -np.inf
        mnpos, mxpos = np.nan, np.nan

        lookformax = True

        for i in np.arange(len(v)):
            this = v[i]
            if this > mx:
                mx = this
                mxpos = x[i]
            if this < mn:
                mn = this
                mnpos = x[i]

            if lookformax:
                if i == len(v) - 1 and mx > mn + d:
                    maxtab.append((mxpos, mx))
                    continue
                if this < mx - d:
                    maxtab.append((mxpos, mx))
                    mn = this
                    mnpos = x[i]
                    lookformax = False
            else:
                if this > mn + d:
                    mintab.append((mnpos, mn))
                    mx = this
                    mxpos = x[i]
                    lookformax = True

        return np.array(maxtab), np.array(mintab)

    def get_peaks(self):
        self.__init()

        peak_xy, _ = self.__peak_det(self.data, self.delta)
        self.__num_events = len(peak_xy)
        self.__fre = self.__num_events / self.duration_sec
        events = peak_xy.T
        self.__events = events

    def add_event(self, x: int, y=None):
        if y is None:
            y_ = self[x]
        else:
            y_ = y

        self.__events[0].append(x)
        self.__events[1].append(y_)
        self.__num_events += 1
        self.__fre += 1/self.duration_sec

    def adjust_baseline(self):
        self.data -= self.baseline
        self.__baseline = np.zeros_like(self.data)
        if self.__events is not None:
            self.get_peaks()

    def kinetics(self):
        p_index = self.events[0].astype(np.int_)
        self.__fwhm, yhalf, x1half, x2half = peak_widths(self.data, p_index)
        self.__fwhm = self.__fwhm/self.rate
        width10, y10, x110, x210 = peak_widths(self.data, p_index, rel_height=0.8)
        width90, y90, x190, x290 = peak_widths(self.data, p_index, rel_height=0.2)
        self.__rise1090 = x190 - x110
        self.__rise1090 = self.__rise1090 / self.rate
        self.__decay1090 = x210 - x290
        self.__decay1090 = self.__decay1090/ self.rate
