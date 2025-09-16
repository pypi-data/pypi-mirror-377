"""mcms-benchs: A toolbox that provides a common framework for benchmarks of multi-component signal processing methods.

Copyright (C) 2024  Juan Manuel Miramont

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from numpy import pi as pi
import scipy.signal as sg
import string
from math import factorial


class Signal(np.ndarray):
    """
    A class that emulates a signal by behaving like a Numpy array for practical
    purposes but containing information of the signal such as the number of components
    and their instantaneous frequency (IF). This class is used in two ways:

    1. As a way of creating more complicated signals (i.e. with more components) and
    automatically stablish the number of components and IF by just defining them for
    the more simple, monocomponent signals. This way, when linearly combining two signals
    all the information regarding the combined components and their instantaneous
    frequencies is saved and is accessible from the final signal.

    2. As a way of wrap up information of the signal when passed to a method in the
    Benchmark class. The idea is that methods called by this latter class only receive
    a signal and parameters for the method. Therefore, by encapsulating the information
    of the signal in the Signal object, the method can use it while keep treating the
    received signal as a regular numpy array.

    A Signal class object has four attributes that differentiate it from a regular
    numpy array:
    1. comps: A list with each of the individual components combined to produce the
    signal.
    2. insft: A list with each of the individual components' instantenous frequency.
    The length of this list is the same as the comps list.
    3. ncomps: A numpy array indicating the number of components present in each time
    sample of the signal.
    4. total_comps: The total amount of components present within the duration of the
    signal. This is simply the length of comps.

    Methods
    -------

        def add_comp(self, new_comp, **kwargs)
        def add_instf(self, new_instf, **kwargs)


    """

    def __new__(
        subtype, array, instf=None, buffer=None, offset=0, strides=None, order=None
    ):

        dtype = array.dtype
        shape = array.shape
        # Create the ndarray instance of our type, given the usual
        # ndarray input arguments.  This will call the standard
        # ndarray constructor, but return an object of our type.
        # It also triggers a call to InfoArray.__array_finalize__
        obj = super().__new__(subtype, shape, dtype, buffer, offset, strides, order)
        # set the new 'info' attribute to the value passed

        if len(array) == 1:
            return array

        # Get the values of the ndarray
        obj[:] = array[:]

        # Add new attributes to the object
        obj._comps = [
            array.copy(),
        ]
        obj._ncomps = None
        obj._total_comps = None

        if instf is None:
            obj._instf = [
                np.zeros_like(array),
            ]
        else:
            obj._instf = [
                instf.copy(),
            ]

        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # ``self`` is a new object resulting from
        # ndarray.__new__(InfoArray, ...), therefore it only has
        # attributes that the ndarray.__new__ constructor gave it -
        # i.e. those of a standard ndarray.
        #
        # We could have got to the ndarray.__new__ call in 3 ways:
        # From an explicit constructor - e.g. InfoArray():
        #    obj is None
        #    (we're in the middle of the InfoArray.__new__
        #    constructor, and self.info will be set when we return to
        #    InfoArray.__new__)
        if obj is None:
            return
        # From view casting - e.g arr.view(InfoArray):
        #    obj is arr
        #    (type(obj) can be InfoArray)
        # From new-from-template - e.g infoarr[:3]
        #    type(obj) is InfoArray
        #
        # Note that it is here, rather than in the __new__ method,
        # that we set the default value for 'info', because this
        # method sees all creation of default objects - with the
        # InfoArray.__new__ constructor, but also with
        # arr.view(InfoArray).
        self._comps = getattr(
            obj,
            "_comps",
            [
                obj,
            ],
        )
        self._instf = getattr(obj, "_instf", list())
        self._ncomps = getattr(obj, "_ncomps", None)
        self._total_comps = getattr(obj, "_total_comps", None)
        # self._instf = getattr(obj, '_ncomps', [obj, ])

        # [np.zeros_like(self._comps[0]),]

        # self._ncomps = getattr(obj,'_ncomps', None)
        # We do not need to return anything

    # def __init__(self, array=None, instf=None):
    #     self.comps = list()
    #     self.comps.append(array)

    #     if instf is None:
    #         self.instf = np.zeros_like(array)
    #     else:
    #         self.instf = instf

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        args = []

        for i, input_ in enumerate(inputs):
            # args.append(input_)
            if isinstance(input_, Signal):
                aux = input_.view(np.ndarray)
                if len(aux) == 1:
                    aux = aux[0]

                args.append(aux)
            else:
                args.append(input_)

        results = super().__array_ufunc__(ufunc, method, *tuple(args), **kwargs)

        if isinstance(results, np.ndarray):  # and ufunc.__name__ =='__add__':
            results = results.view(Signal)
            results._comps = []
            results._instf = []
            for ip in [a_signal for a_signal in inputs if isinstance(a_signal, Signal)]:
                for cp, instf in zip([*ip.comps], [*ip.instf]):
                    results.add_comp(cp, instf=instf)

        return results

    # Other functions from numpy.ndarray that we need.
    # TODO: Generalize these methods on one super() based function.
    def std(self, axis, dtype, out, ddof, **kwargs):
        return self.view(np.ndarray).std(
            axis=axis, dtype=dtype, out=out, ddof=ddof, **kwargs
        )

    def var(self, axis, dtype, out, ddof, **kwargs):
        return self.view(np.ndarray).var(
            axis=axis, dtype=dtype, out=out, ddof=ddof, **kwargs
        )

    @property
    def total_comps(self):
        if self._total_comps is None:
            self._total_comps = len(self._comps)
        return self._total_comps

    @total_comps.setter
    def total_comps(self, value):
        self._total_comps = value

    @property
    def ncomps(self):
        if self._ncomps is None:
            self.component_counter()
        return self._ncomps

    @ncomps.setter
    def ncomps(self, value):
        self._ncomps = value

    @property
    def comps(self):
        return self._comps

    @property
    def instf(self):
        return self._instf

    @instf.setter
    def instf(self, value):
        self._instf = value



    def add_comp(self, new_comp, **kwargs):
        """Add a new component, potentially with its instantaneous frequency. This
        latter can be added later.

        Args:
            new_comp (numpy.ndarray): New component to add.
            instf (numpy.ndarray): The instantaneous frequency corresponding to new_comp
        """

        self._comps.append(new_comp)
        if "instf" in kwargs.keys():
            self._instf.append(kwargs["instf"])

    def add_instf(self, new_instf, **kwargs):
        """Add a new instantaneous frequency.

        Args:
            new_instf (numpy.ndarray): A vector with the instantaneous frequency.
        """
        self._instf.append(new_instf)

    def component_counter(self):
        """This functions counts the number of components per time sample, and set the
        corresponding attribute self._ncomps.
        """
        N = len(self)
        cc = np.zeros((N,), dtype=int)
        th = 0.0
        for component in self._comps:
            for i in range(N):
                if np.sum(np.abs(component[i])) > th:
                    cc[i] += 1
        self._ncomps = cc

    def get_info(self):
        return {
            "ndarray": self.view(np.ndarray),
            "ncomps": self.ncomps,
            "total_comps": self.total_comps,
            "instf": self.instf,
        }


class SignalBank:
    """
    Create a bank of signals. This class encapsulates the signal generation code,
    and returns different methods to generate signals as well as a dictionary of those
    methods that can be used later. Methods starting with "signal" generate
    monocomponent signals. Methods starting with "signal_mc" generate multicomponent
    signals.

    Both types of signals al generated with a length "N" passed as input parameter at
    the moment of instantiation. Signals are separated at least N^0.5 samples from the
    borders of the time-frequency plane in order to reduce border effects.

    Methods
    -------
        def check_frec_margins(self, instf):
            Check that the instantaneous frequency (if available) of a generated signal
            is within certain margins to avoid aliasing and border effects.

        def generate_signal_dict(self):
            This function is used by the class constructor to generate a dictionary of
            signals. The keys of this dictionary are the name of the signals or
            "signal_id" that is used to indicate the benchmark which signals use to
            compare methods.

        def get_signal_id(self):
            Get the keys of the dictionary of signals generated by the function
            "generate_signal_dict()" when needed.

        def signal_linear_chirp(self, a=None, b=None, instfreq = False):
            Returns a linear chirp, the instantaneous frequency of which is a linear
            function with slope "a" and initial normalized frequency "b".

        def signal_mc_crossing_chirps(self):
            Returns a multi component signal with two chirps crossing, i.e. two chirps
            whose instantaneous frequency coincide in one point of the time frequency
            plane.

        def signal_mc_pure_tones(self, ncomps=5, a1=None, b1=None):
            Generates a multicomponent signal comprising several pure tones harmonically
            separated, i.e. tones are ordered from lower to higher frequency and each
            one has an instantaneous frequency that is an entire multiple of that of the
            previous tone.

        def signal_mc_multi_linear(self, ncomps=5):
            Generates a multicomponent signal with multiple linear chirps.

        def signal_tone_damped(self):
            Generates a damped tone whose normalized frequency is 0.25.

        def signal_tone_sharp_attack(self):
            Generates a damped tone that is modulated with a rectangular window.

        def signal_cos_chirp(self, omega=1.5, a1=1, f0=0.25, a2=0.125, checkinstf=True):
            Generates a cosenoidal chirp, the instantenous frequency of which is given
            by the formula: "f0 + a1*cos(2*pi*omega)", and the maximum amplitude of
            which is determined by "a2".

        def signal_mc_double_cos_chirp(self):
            Generates a multicomponent signal with two cosenoidal chirps.

        def signal_mc_cos_plus_tone(self):
            Generates a multicomponent signal comprised by two cosenoidal chirps and a
            single tone.

        def signal_mc_synthetic_mixture(self):
            Generates a multicomponent signal with different types of components.

        def signal_hermite_function(self, order = 18, t0 = 0.5, f0 = 0.25):
            Generates a round hermite function of a given order. The spectrogram of
            Hermite functions are given by an annular ridge in the time frequency plane,
            the center of which is given by (t0,f0).

        def signal_hermite_elipse(self, order = 30, t0 = 0.5, f0 = 0.25):
            Generates a non-round Hermite function of a given order. The spectrogram of
            Hermite functions are given by an elipsoidal ridge in the time frequency
            plane the center of which is given by (t0,f0).

        def signal_mc_triple_impulse(self, Nimpulses = 3):
            Generates three equispaced impulses in time.

        def signal_mc_impulses(self, Nimpulses = 7):
            Generates equispaced impulses in time.

        def signal_exp_chirp(self, finit=None, fend=None, exponent=2, r_instf=False):
            Generates an exponential chirp.

        def signal_mc_exp_chirps(self):
            Generates a multicomponent signal comprising three exponential chirps.

        def signal_mc_multi_cos(self):
            Generates a multicomponent signal comprising three cosenoidal chirps with
            different frequency modulation parameters.

        def signal_mc_synthetic_mixture_2(self):
            Generates a multicomponent signal with different types of components.

        def signal_mc_on_off_tones(self):
            Generates a multicomponent signal comprising components that "born" and
            "die" at different times.

        def signal_mc_synthetic_mixture_3(self):
            Generates a multicomponent signal with different types of components.

        def get_all_signals(self):
            Returns an array of shape [K,N] where K is the number of signals generated
            by this signal bank, and N is the length of the signals.
    """

    def __init__(self, N=2**8, Nsub=None, return_signal=False):
        """Builds a dictionary of functions that return multiple signals.
        Args:
            N (int, optional): Length of the signals. Defaults to 2**8.
            Nsub (int, optional): Generates signals of length Nsub,
            then zero pads the vector to reach length N. Defaults to 2**8.
            return_signal (bool, optional): If True, functions will return a Signal
            object, that encapsulates more information of the signal such as the number
            of components, each individual component and their instantaneous frequency.
        """
        self.return_signal = return_signal

        self.N = N
        if Nsub is None:
            self.tmin = int(np.sqrt(N))
            self.tmax = self.N - self.tmin
            self.Nsub = self.tmax - self.tmin
        else:
            self.Nsub = Nsub
            self.tmin = (self.N - self.Nsub) // 2
            self.tmax = self.tmin + Nsub

        # self.fmin = 1.0*np.sqrt(N)/N
        # self.fmax = 0.5-self.fmin
        # self.fmid = (self.fmax-self.fmin)/2 + self.fmin

        self.fmin = 0.07
        self.fmax = 0.5 - self.fmin
        self.fmid = 0.25

        # print(self.fmin)
        # print(self.fmax)

        self.generate_signal_dict()

    # TODO
    def check_inst_freq(self, instf):
        """Check that the instantaneous frequency (if available) of a generated signal
        is within certain margins to avoid aliasing and border effects.

        Args:
            instf (numpy.ndarray): Instantaneous frequency of a signal.
        """

        # if np.all(instf<=self.fmax):
        #     print('Warning: instf>fmax')
        # if np.all(instf>=self.fmin):
        #     print('Warning: instf<fmin')
        return True

    def generate_signal_dict(self):
        """This function is used by the class constructor to generate a dictionary of
        signals. The keys of this dictionary are the name of the signals or "signal_id"
        that is used to indicate the benchmark which signals use to compare methods.

        Returns:
            dict: Dictionary of functions that returns a signal when called.
        """

        campos = dir(self)
        fun_names = [fun_name for fun_name in campos if fun_name.startswith("signal_")]
        signal_ids = [
            string.capwords(fun_name[7::], sep="_").replace("_", "")
            for fun_name in fun_names
        ]

        self.signalDict = dict()
        for i, signal_id in enumerate(signal_ids):
            try:
                self.signalDict[signal_id] = getattr(self, fun_names[i])()

            except BaseException as err:
                self.signalDict[signal_id] = None

        return self.signalDict

    def get_signal_id(self):
        """Get the keys of the dictionary of signals generated by the function
        "generate_signal_dict()" when needed.

        Returns:
            tuple: Tuple with the keys of a dictionary of signals.
        """

        return self.SignalDict.keys()

    def get_all_signals(self):
        """Returns an array of shape [K,N] where K is the number of signals generated
        by this signal bank, and N is the length of the signals.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        signals = np.zeros((len(self.signalDict), self.N))
        for k, key in enumerate(self.signalDict):
            signals[k] = self.signalDict[key]()
        return signals

    # Monocomponent signals --------------------------------------------------------

    def _signal_linear_chirp(self, a=None, b=None, phi=0, instfreq=False):
        """Returns a linear chirp, the instantaneous frequency of which is a linear
        function with slope "a" and initial normalized frequency "b".


        Args:
            a (int, optional): Slope of the instantaneous frequency. Defaults to None.
            b (int, optional): Initial instantaneous frequency. Defaults to None.
            instfreq (bool, optional): When True, returns a vector with the
            instantaneous frequency. Defaults to False.

        Returns:
            list or ndarray: If input parameter "instfreq" is True, returns the a list
            of ndarray type objects with the signal and its instantaneous frequency.
        """

        N = self.N

        if a is None:
            a = self.fmax - self.fmin
        if b is None:
            b = self.fmin

        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub

        tsub = np.arange(Nsub)
        instf = b + a * tsub / Nsub

        if not instfreq:
            self.check_inst_freq(instf)

        phase = np.cumsum(instf)

        x = np.cos(2 * pi * phase + phi) * sg.windows.tukey(Nsub, 0.25)
        signal = np.zeros((N,))
        signal[tmin:tmax] = x

        emb_instf = np.zeros_like(signal)
        emb_instf[tmin:tmax] = instf

        # Cast to Signal class.
        signal = Signal(array=signal, instf=emb_instf)

        if instfreq:
            return signal, instf, tmin, tmax
        else:
            return signal

    def _signal_tone_damped(self):
        """Generates a damped tone whose normalized frequency is 0.25.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        eps = 1e-6
        t = np.arange(N) + eps
        c = 1 / N / 10
        prec = 1e-1  # Precision at sample N for the envelope.
        alfa = -np.log(prec * N / ((N - c) ** 2)) / N
        e = np.exp(-alfa * t) * ((t - c) ** 2 / t)
        e[0] = 0
        chirp = self._signal_linear_chirp(a=0, b=0.25)
        return e * chirp

    def _signal_tone_sharp_attack(self):
        """Generates a damped tone that is modulated with a rectangular window.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        dumpcos = self.signal_tone_damped()
        indmax = np.argmax(dumpcos)
        dumpcos[0:indmax] = 0
        return dumpcos

    def _signal_exp_chirp(self, finit=None, fend=None, exponent=2, r_instf=False):
        """Generates an exponential chirp.

        Args:
            finit (float, optional): Initial normalized frequency. Defaults to None.
            fend (float, optional): End normalized frequency. Defaults to None.
            exponent (int, optional): Exponent. Defaults to 2.
            r_instf (bool, optional): When True returns the instantaneous frequency
            along with the signal. Defaults to False.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub
        tsub = np.arange(Nsub) / Nsub

        if finit is None:
            finit = 1.5 * self.fmin

        if fend is None:
            fend = self.fmax

        instf = finit * np.exp(np.log(fend / finit) * tsub**exponent)

        if not r_instf:
            self.check_inst_freq(instf)

        phase = np.cumsum(instf)
        x = np.cos(2 * pi * phase)
        signal = np.zeros((N,))
        signal[tmin:tmax] = x * sg.windows.tukey(Nsub, 0.25)

        emb_instf = np.zeros_like(signal)
        emb_instf[tmin:tmax] = instf

        # Cast to Signal class.
        signal = Signal(array=signal, instf=emb_instf)

        if r_instf:
            return signal, instf, tmin, tmax
        else:
            return signal

    def _signal_cos_chirp(self, omega=1.2, a1=0.5, f0=0.25, a2=0.125, checkinstf=True):
        """Generates a cosenoidal chirp, the instantenous frequency of which is given by
        the formula: "f0 + a1*cos(2*pi*omega)", and the maximum amplitude of which is
        determined by "a2".

        Args:
            omega (float, optional): Frequency of the instantaneous frequency.
            Defaults to 1.5.
            a1 (int, optional): Amplitude of the frequency modulation Defaults to 1.
            f0 (float, optional): Central frequency. Defaults to 0.25.
            a2 (float, optional): Amplitude of the signal. Defaults to 0.125.
            checkinstf (bool, optional): If True checks that dhe instantaneous frequency
            of the signal is within the limits. Defaults to True.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub
        tsub = np.arange(Nsub)
        instf = f0 + a2 * np.cos(2 * pi * omega * tsub / Nsub - pi * omega)

        if checkinstf:
            self.check_inst_freq(instf)

        phase = np.cumsum(instf)
        x = a1 * np.cos(2 * pi * phase) * sg.windows.tukey(Nsub, 0.25)
        signal = np.zeros((N,))
        signal[tmin:tmax] = x

        emb_instf = np.zeros_like(signal)
        emb_instf[tmin:tmax] = instf

        # Cast to Signal class.
        signal = Signal(array=signal, instf=emb_instf)

        return signal

    # Output monocomponent signals -------------------------------------------------
    def signal_linear_chirp(self, a=None, b=None, instfreq=False):
        """Returns a linear chirp, the instantaneous frequency of which is a linear
        function with slope "a" and initial normalized frequency "b".


        Args:
            a (int, optional): Slope of the instantaneous frequency. Defaults to None.
            b (int, optional): Initial instantaneous frequency. Defaults to None.
            instfreq (bool, optional): When True, returns a vector with the
            instantaneous frequency. Defaults to False.

        Returns:
            list or ndarray: If input parameter "instfreq" is True, returns the a list
            of ndarray type objects with the signal and its instantaneous frequency.
        """

        signal = self._signal_linear_chirp(a=a, b=b, instfreq=instfreq)
        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_tone_damped(self):
        """Generates a damped tone whose normalized frequency is 0.25.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        eps = 1e-6
        t = np.arange(N) + eps
        c = 1 / N / 10
        prec = 1e-1  # Precision at sample N for the envelope.
        alfa = -np.log(prec * N / ((N - c) ** 2)) / N
        e = np.exp(-alfa * t) * ((t - c) ** 2 / t)
        e[0] = 0
        chirp = self._signal_linear_chirp(a=0, b=0.25)
        signal = e * chirp

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    def signal_tone_sharp_attack(self):
        """Generates a damped tone that is modulated with a rectangular window.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        signal = self.signal_tone_damped()
        indmax = np.argmax(signal)
        signal[0:indmax] = 0

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    def signal_exp_chirp(self, finit=None, fend=None, exponent=2, r_instf=False):
        """Generates an exponential chirp.

        Args:
            finit (float, optional): Initial normalized frequency. Defaults to None.
            fend (float, optional): End normalized frequency. Defaults to None.
            exponent (int, optional): Exponent. Defaults to 2.
            r_instf (bool, optional): When True returns the instantaneous frequency
            along with the signal. Defaults to False.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """
        signal = self._signal_exp_chirp(
            finit=finit, fend=fend, exponent=exponent, r_instf=r_instf
        )
        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_cos_chirp(self, omega=1.2, a1=0.5, f0=0.25, a2=0.125, checkinstf=True):
        """Generates a cosenoidal chirp, the instantenous frequency of which is given by
        the formula: "f0 + a1*cos(2*pi*omega)", and the maximum amplitude of which is
        determined by "a2".

        Args:
            omega (float, optional): Frequency of the instantaneous frequency.
            Defaults to 1.5.
            a1 (int, optional): Amplitude of the frequency modulation Defaults to 1.
            f0 (float, optional): Central frequency. Defaults to 0.25.
            a2 (float, optional): Amplitude of the signal. Defaults to 0.125.
            checkinstf (bool, optional): If True checks that dhe instantaneous frequency
            of the signal is within the limits. Defaults to True.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """
        signal = self._signal_cos_chirp(
            omega=omega, a1=a1, f0=f0, a2=a2, checkinstf=checkinstf
        )
        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    # Multicomponent signals here --------------------------------------------------

    def signal_mc_parallel_chirps(self):
        comp1 = self._signal_linear_chirp(a=0.1, b=0.15)
        comp2 = self._signal_linear_chirp(a=0.1, b=0.25)
        signal = comp1 + comp2

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    def signal_mc_parallel_chirps_unbalanced(self):
        comp1 = self._signal_linear_chirp(a=0.1, b=0.15, instfreq=False)
        comp2 = self._signal_linear_chirp(a=0.1, b=0.25, instfreq=False)
        signal = comp1 + 0.2 * comp2

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    def signal_mc_on_off_2(self):
        chirp1 = self._signal_linear_chirp(a=0.1, b=0.10, instfreq=False)
        chirp2a = self._signal_linear_chirp(a=0.1, b=0.20, instfreq=False)
        chirp2b = self._signal_linear_chirp(a=0.1, b=0.20, instfreq=False)
        chirp3 = self._signal_linear_chirp(a=0.1, b=0.30, instfreq=False)

        Nsub = self.N
        N3 = Nsub // 3
        N4 = Nsub // 4
        N7 = Nsub // 7
        N9 = Nsub // 9

        chirp1[0 : 2 * N7] = 0
        chirp1.comps[0][0 : 2 * N7] = 0
        chirp1.instf[0][0 : 2 * N7] = 0

        chirp1[5 * N7 : -1] = 0
        chirp1.comps[0][5 * N7 : -1] = 0
        chirp1.instf[0][5 * N7 : -1] = 0

        chirp1[2 * N7 : 5 * N7] = chirp1[2 * N7 : 5 * N7] * sg.windows.tukey(
            3 * N7, 0.25
        )
        chirp1.comps[0][2 * N7 : 5 * N7] = chirp1[2 * N7 : 5 * N7] * sg.windows.tukey(
            3 * N7, 0.25
        )

        chirp2a[0:N9] = 0
        chirp2a.comps[0][0:N9] = 0
        chirp2a.instf[0][0:N9] = 0
        chirp2a[8 * N9 : -1] = 0
        chirp2a.comps[0][8 * N9 : -1] = 0
        chirp2a.instf[0][8 * N9 : -1] = 0
        chirp2a[4 * N9 : 5 * N9] = 0
        chirp2a.comps[0][4 * N9 : 5 * N9] = 0
        chirp2a.instf[0][4 * N9 : 5 * N9] = 0
        chirp2a[N9 : 4 * N9] = chirp2a[N9 : 4 * N9] * sg.windows.tukey(3 * N9, 0.25)
        chirp2a.comps[0][N9 : 4 * N9] = chirp2a[N9 : 4 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2a._instf[0][5 * N9 : 8 * N9] = 0
        chirp2a.comps[0][5 * N9 : 8 * N9] = 0
        chirp2a[5 * N9 : 8 * N9] = 0

        chirp2b[0:N9] = 0
        chirp2b.comps[0][0:N9] = 0
        chirp2b.instf[0][0:N9] = 0
        chirp2b[8 * N9 : -1] = 0
        chirp2b.comps[0][8 * N9 : -1] = 0
        chirp2b.instf[0][8 * N9 : -1] = 0
        chirp2b[4 * N9 : 5 * N9] = 0
        chirp2b.comps[0][4 * N9 : 5 * N9] = 0
        chirp2b.instf[0][4 * N9 : 5 * N9] = 0
        chirp2b[5 * N9 : 8 * N9] = chirp2b[5 * N9 : 8 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2b.comps[0][5 * N9 : 8 * N9] = chirp2b[5 * N9 : 8 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2b._instf[0][N9 : 4 * N9] = 0
        chirp2b.comps[0][N9 : 4 * N9] = 0
        chirp2b[N9 : 4 * N9] = 0

        signal = chirp1 + chirp2b + chirp2a + chirp3

        if not self.return_signal:
            signal = signal.view(np.ndarray)

        return signal

    def signal_mc_crossing_chirps(self):
        """Returns a multi component signal with two chirps crossing, i.e. two chirps
        whose instantaneous frequency coincide in one point of the time frequency plane.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N

        a = self.fmax - self.fmin
        b = self.fmin

        chirp1 = 0.8 * self._signal_linear_chirp(a=-0.31, b=0.41, phi=0)
        chirp2 = self._signal_linear_chirp(a=0.35, b=0.1, phi=0)

        signal = chirp1 + chirp2

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    # def signal_mc_crossing_chirps_2(self):
    #     """Returns a multi component signal with two chirps crossing, i.e. two chirps
    #     whose instantaneous frequency coincide in one point of the time frequency plane.

    #     Returns:
    #         numpy.ndarray: Returns a numpy array with the signal.
    #     """

    #     N = self.N

    #     a = self.fmax-self.fmin
    #     b = self.fmin

    #     chirp1 = self._signal_linear_chirp(a = -a, b = 0.5 - b)
    #     chirp2 = self._signal_linear_chirp(a = a, b = b)

    #     tmin = self.tmin
    #     tmax = N-tmin
    #     Nsub = tmax-tmin
    #     tsub = np.arange(Nsub)
    #     fmax = self.fmax

    #     signal = np.zeros((N,))
    #     instf0 = np.zeros_like(signal)

    #     omega = 1.5
    #     f0 = 0.5 - b - a*tsub/Nsub
    #     if0 = f0+ 0.02 + 0.02*np.cos(2*pi*omega*tsub/Nsub - pi*omega)
    #     if0 = if0[np.where(if0<fmax)]
    #     self.check_inst_freq(if0)
    #     phase0 = np.cumsum(if0)
    #     x0 = np.zeros_like(signal)
    #     x0[tmin:tmin+len(phase0)] = np.cos(2*pi*phase0)*sg.windows.tukey(len(phase0),0.25)
    #     instf0[tmin:tmin+len(if0)] = if0
    #     chirp1 = Signal(x0, instf=instf0)

    #     signal = chirp1 + chirp2

    #     if not self.return_signal:
    #         return signal.view(np.ndarray)

    #     return signal

    def signal_mc_pure_tones(self, ncomps=5, a1=None, b1=None, c0=0.0):
        """Generates a multicomponent signal comprising several pure tones harmonically
        separated, i.e. tones are ordered from lower to higher frequency and each one
        has an instantaneous frequency that is an entire multiple of that of the
        previous tone.

        Args:
            ncomps (int, optional): Number of components. Defaults to 5.
            a1 (float, optional): Slope of chirps. Defaults to 0.
            b1 (float, optional): Frequency of the first tone. Defaults to None.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        k = 1
        aux = np.zeros((N,))
        max_freq = self.fmax

        if a1 is None:
            a1 = 0
        if b1 is None:
            b1 = self.fmid / 2
            if b1 < self.fmin:
                b1 = self.fmin

        signal = self._signal_linear_chirp(a=a1, b=b1 + c0)

        for i in range(1, ncomps):
            chirp = self._signal_linear_chirp(a=a1 * (i + 1), b=b1 * (i + 1) + c0)
            if np.max(chirp.instf[0]) >= max_freq:
                break
            signal = signal + chirp

        # for i in range(ncomps):
        #     chirp, instf, tmin, _ = self.signal_linear_chirp(a = a1*(i+1),
        #                                                      b = b1*(i+1),
        #                                                      instfreq=True)
        #     if instf[0] >= max_freq:
        #         break

        #     idx = np.where(instf < max_freq)[0] + tmin -1
        #     tukwin = sg.windows.tukey(idx.shape[0],0.5)
        #     chirp[idx] = chirp[idx]*tukwin
        #     idx = np.where(instf >= max_freq)[0] + tmin -1
        #     chirp[idx] = tukwin[-1]

        #     aux += chirp

        if not self.return_signal:
            return signal.view(np.ndarray)

        return signal

    def signal_mc_multi_linear(self, ncomps=5):
        """Generates a multicomponent signal with multiple linear chirps.

        Args:
            ncomps (int, optional): Number of components. Defaults to 5.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        a1 = self.fmin / 2
        b1 = self.fmin
        signal = self.signal_mc_pure_tones(ncomps=ncomps, a1=a1, b1=b1)

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_multi_linear_2(self, ncomps=5):
        """Generates a multicomponent signal with multiple linear chirps.

        Args:
            ncomps (int, optional): Number of components. Defaults to 5.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        a1 = self.fmin / 2
        b1 = self.fmin / 3
        signal = self.signal_mc_pure_tones(ncomps=ncomps, a1=a1, b1=b1, c0=self.fmin)

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_double_cos_chirp(self):
        """Generates a multicomponent signal with two cosenoidal chirps.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        t = np.arange(N) / N
        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub
        tsub = np.arange(Nsub)
        omega1 = 1.5
        omega2 = 1.8

        chirp1 = self._signal_cos_chirp(
            omega=omega1, a1=1.0, f0=self.fmax - 0.075, a2=0.05
        )

        chirp2 = self._signal_cos_chirp(
            omega=omega2, a1=1.0, f0=self.fmin + 0.075, a2=0.06
        )

        # instf1 = self.fmax-0.075 + 0.05*np.cos(2*pi*omega1*tsub/Nsub - pi*omega1)
        # self.check_inst_freq(instf1)
        # instf2 = self.fmin+0.075 + 0.06*np.cos(2*pi*omega2*tsub/Nsub - pi*omega2)
        # self.check_inst_freq(instf2)

        # phase1 = np.cumsum(instf1)
        # phase2 = np.cumsum(instf2)
        # x = np.cos(2*pi*phase1) + np.cos(2*pi*phase2)
        # x = x*sg.windows.tukey(Nsub,0.25)
        # signal = np.zeros((N,))
        # signal[tmin:tmax] = x

        signal = chirp1 + chirp2

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_cos_plus_tone(self):
        """Generates a multicomponent signal comprised by two cosenoidal chirps and a
        single tone.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        omega1 = 1.5
        omega2 = 1.8

        chirp1 = self._signal_cos_chirp(
            omega=omega1, a1=1.0, f0=self.fmax - 0.05, a2=0.04
        )

        chirp2 = self._signal_cos_chirp(omega=omega2, a1=1.0, f0=self.fmid, a2=0.04)

        chirp3 = self._signal_linear_chirp(a=0, b=1.8 * self.fmin)

        # instf1 = self.fmax-0.05 + 0.04*np.cos(2*pi*omega1*tsub/Nsub - pi*omega1)
        # self.check_inst_freq(instf1)
        # instf2 = self.fmid + 0.04*np.cos(2*pi*omega2*tsub/Nsub - pi*omega2)
        # self.check_inst_freq(instf2)
        # instf3 = 1.8*self.fmin * np.ones((Nsub,))
        # self.check_inst_freq(instf3)

        # phase1 = np.cumsum(instf1)
        # phase2 = np.cumsum(instf2)
        # phase3 = np.cumsum(instf3)
        # x = np.cos(2*pi*phase1) + np.cos(2*pi*phase2) + np.cos(2*pi*phase3)
        # x = x*sg.windows.tukey(Nsub,0.25)
        # signal = np.zeros((N,))
        # signal[tmin:tmax] = x

        signal = chirp1 + chirp2 + chirp3

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_multi_cos(self):
        """Generates a multicomponent signal comprising three cosenoidal chirps with
        different frequency modulation parameters.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        x1 = self._signal_cos_chirp(omega=8, a1=1, f0=self.fmin + 0.04, a2=0.03)
        x2 = self._signal_cos_chirp(omega=6, a1=1, f0=self.fmid, a2=0.02)
        x3 = self._signal_cos_chirp(omega=4, a1=1, f0=self.fmax - 0.03, a2=0.02)
        # x4 = self.signal_cos_chirp(omega = 10, a1=1, f0=0.42, a2=0.05)
        signal = x1 + x2 + x3

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_multi_cos_2(self):
        """Generates a multicomponent signal comprising three cosenoidal chirps with
        different frequency modulation parameters.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        x1 = self._signal_cos_chirp(omega=5, a1=1.5, f0=self.fmin + 0.04, a2=0.03)
        x2 = self._signal_cos_chirp(omega=5, a1=1.2, f0=self.fmid, a2=0.02)
        x3 = self._signal_cos_chirp(omega=5, a1=1, f0=self.fmax - 0.03, a2=0.02)
        # x4 = self.signal_cos_chirp(omega = 10, a1=1, f0=0.42, a2=0.05)
        signal = x1 + x2 + x3

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_synthetic_mixture(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        t = np.arange(N) / N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        fmax = self.fmax

        signal = np.zeros((N,))
        instf0 = np.zeros_like(signal)
        instf1 = np.zeros_like(signal)
        instf2 = np.zeros_like(signal)

        omega = 7
        f0 = self.fmin + 0.07 * tsub / Nsub
        f1 = 1.2 * self.fmin + 0.25 * tsub / Nsub
        f2 = 1.3 * self.fmin + 0.53 * tsub / Nsub

        if0 = f0 + 0.02 + 0.02 * np.cos(2 * pi * omega * tsub / Nsub - pi * omega)
        if1 = f1 + 0.02 + 0.02 * np.cos(2 * pi * omega * tsub / Nsub - pi * omega)
        if2 = f2 + 0.02 + 0.02 * np.cos(2 * pi * omega * tsub / Nsub - pi * omega)
        if0 = if0[np.where(if0 < fmax)]
        if1 = if1[np.where(if1 < fmax)]
        if2 = if2[np.where(if2 < fmax)]

        self.check_inst_freq(if0)
        self.check_inst_freq(if1)
        self.check_inst_freq(if2)

        phase0 = np.cumsum(if0)
        phase1 = np.cumsum(if1)
        phase2 = np.cumsum(if2)

        x0 = np.zeros_like(signal)
        x1 = np.zeros_like(signal)
        x2 = np.zeros_like(signal)

        x0[tmin : tmin + len(phase0)] = np.cos(2 * pi * phase0) * sg.windows.tukey(
            len(phase0), 0.25
        )
        x1[tmin : tmin + len(phase1)] = np.cos(2 * pi * phase1) * sg.windows.tukey(
            len(phase1), 0.25
        )
        x2[tmin : tmin + len(phase2)] = np.cos(2 * pi * phase2) * sg.windows.tukey(
            len(phase2), 0.25
        )

        instf0[tmin : tmin + len(if0)] = if0
        instf1[tmin : tmin + len(if1)] = if1
        instf2[tmin : tmin + len(if2)] = if2

        chirp0 = Signal(x0, instf=instf0)
        chirp1 = Signal(x1, instf=instf1)
        chirp2 = Signal(x2, instf=instf2)

        # signal = x0+x1+x2

        signal = chirp0 + chirp1 + chirp2

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_synthetic_mixture_2(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        def rect_window(N, ti, te):
            rw = np.zeros((N,))
            rw[ti:te] = 1
            return rw

        N = self.N
        t = np.arange(N)
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        fmax = self.fmax
        fmin = self.fmin

        tt = Nsub // 2
        t_init = tmin

        f_init = (0.25 - fmin) / 2 + fmin
        f_end = fmax
        m = (f_end - f_init) / tt

        instf1 = (m * (t - t_init) + f_init) * rect_window(N, t_init, t_init + tt)
        phase1 = np.cumsum(instf1)
        x1 = np.cos(2 * pi * phase1) * rect_window(N, t_init, t_init + tt)
        x1[t_init : t_init + tt] *= sg.windows.tukey(tt, 0.4)

        c = 1 / tt / 10
        prec = 1e-1  # Precision at sample N for the envelope.
        alfa = -np.log(prec * tt / ((tt - c) ** 2)) / tt
        e = np.exp(-alfa * np.arange(tt)) * (
            (np.arange(tt) - c) ** 2 / (np.arange(tt) + 1e-15)
        )
        e[0] = 0
        e /= np.max(e)

        t_init += tt // 2
        instf2 = (m * (t - t_init) + f_init) * rect_window(N, t_init, t_init + tt)
        phase2 = np.cumsum(instf2)
        x2 = np.cos(2 * pi * phase2) * rect_window(N, t_init, t_init + tt)
        x2[t_init : t_init + tt] *= sg.windows.tukey(tt, 0.25) * e

        t_init += tt // 2
        instf3 = (m * (t - t_init) + f_init) * rect_window(N, t_init, t_init + tt)
        phase3 = np.cumsum(instf3)
        x3 = np.cos(2 * pi * phase3) * rect_window(N, t_init, t_init + tt)
        x3[t_init : t_init + tt] *= sg.windows.tukey(tt, 0.25) * e[-1::-1]

        x4 = np.cos(2 * pi * fmin * np.ones((N,)) * t) * rect_window(N, tmin, tmax)
        x4[tmin:tmax] *= sg.windows.tukey(Nsub, 0.75)
        instf4 = fmin * np.ones((N,))

        signal = (
            Signal(x1, instf=instf1)
            + Signal(x2, instf=instf2)
            + Signal(x3, instf=instf3)
            + Signal(x4, instf=instf4)
        )

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_synthetic_mixture_5(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub
        tmid = Nsub // 2
        # tmid = tmid +(tmax-tmid)//5
        tsub = np.arange(Nsub)
        signal = np.zeros((N,))

        if1 = 1 * self.fmin + 4.0 * (tsub / Nsub - 0.05) ** 2
        if1 = if1[np.where(if1 < self.fmax)]
        if1 = if1[np.where(self.fmin < if1)]
        phase1 = np.cumsum(if1)
        x = np.cos(2 * pi * phase1) * sg.windows.tukey(len(phase1), 0.5)
        chirp1 = np.zeros_like(signal)
        chirp1[tmin : tmin + len(x)] = x
        instf1 = np.zeros_like(signal)
        instf1[tmin : tmin + len(x)] = if1

        N = self.N
        tmin = 12 * self.tmin
        tmax = N - self.tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        fmax = self.fmax

        signal = np.zeros((N,))
        instf2 = np.zeros_like(signal)
        omega = 4
        f2 = 1.2 * self.fmin + 0.1 * tsub / Nsub
        if2 = f2 + 0.035 + 0.02 * np.cos(2 * pi * omega * tsub / Nsub - pi * omega)
        if2 = if2[np.where(if2 < fmax)]
        phase2 = np.cumsum(if2)
        x2 = np.zeros_like(signal)
        x2[tmin : tmin + len(phase2)] = np.cos(2 * pi * phase2) * sg.windows.tukey(
            len(phase2), 0.25
        )
        instf2[tmin : tmin + len(if2)] = if2

        tmin = 12 * self.tmin
        tmax = N - self.tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        instf3 = np.zeros_like(signal)
        omega = 5
        f3 = 1.2 * self.fmin + 0.2 * tsub / Nsub
        if3 = f3 + 0.17  # + 0.02*np.cos(2*pi*omega*tsub/Nsub - pi*omega)
        if3 = if3[np.where(if3 < fmax)]
        phase3 = np.cumsum(if3)
        x3 = np.zeros_like(signal)
        x3[tmin : tmin + len(phase3)] = np.cos(2 * pi * phase3) * sg.windows.tukey(
            len(phase3), 0.25
        )
        instf3[tmin : tmin + len(if3)] = if3

        signal = (
            Signal(chirp1, instf=instf1)
            + Signal(x2, instf=instf2)
            + Signal(x3, instf=instf3)
            # + Signal(chirp4, instf=None)
        )

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_synthetic_mixture_3(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = self.tmax
        Nsub = self.Nsub
        tmid = Nsub // 2
        # tmid = tmid +(tmax-tmid)//5
        tsub = np.arange(Nsub)
        signal = np.zeros((N,))

        if1 = 1 * self.fmin + 1 * (tsub / Nsub - 0.05) ** 2
        if1 = if1[np.where(if1 < self.fmax)]
        if1 = if1[np.where(self.fmin < if1)]
        phase1 = np.cumsum(if1)
        x = np.cos(2 * pi * phase1) * sg.windows.tukey(len(phase1), 0.5)
        chirp1 = np.zeros_like(signal)
        chirp1[tmin : tmin + len(x)] = x
        instf1 = np.zeros_like(signal)
        instf1[tmin : tmin + len(x)] = if1

        if2 = np.ones((Nsub,)) * (self.fmid - self.fmin) / 2
        if2 = if2[tmid::]
        phase2 = np.cumsum(if2)
        x2 = np.cos(2 * pi * phase2) * sg.windows.tukey(len(phase2), 0.1)
        chirp2 = np.zeros_like(signal)
        chirp2[tmid : tmid + len(x2)] = x2
        instf2 = np.zeros_like(signal)
        instf2[tmid : tmid + len(x2)] = if2

        instf3 = np.ones((N,)) * (2 * (self.fmid - self.fmin) / 3 + self.fmid)
        phase3 = np.cumsum(instf3)
        tloc = 5 * N // 7
        chirp3 = (
            3
            * np.cos(2 * pi * phase3)
            * np.exp(-np.pi * (np.arange(N) - tloc) ** 2 / (N / 8))
        )

        instf4 = np.ones((N,)) * ((self.fmid - self.fmin) / 3 + self.fmid)
        phase4 = np.cumsum(instf4)
        tloc = 6 * N // 7
        chirp4 = (
            5
            * np.cos(2 * pi * phase4)
            * np.exp(-np.pi * (np.arange(N) - tloc) ** 2 / (N / 8))
        )

        signal = (
            Signal(chirp1, instf=instf1)
            + Signal(chirp2, instf=instf2)
            + Signal(chirp3, instf=None)
            + Signal(chirp4, instf=None)
        )

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_synthetic_mixture_4(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        def rect_window(N, ti, te):
            rw = np.zeros((N,))
            rw[ti:te] = 1
            return rw

        N = self.N
        t = np.arange(N)
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        fmax = self.fmax
        fmin = self.fmin

        tt = int(Nsub // 2.5)
        t_init = 4 * tmin

        f_init = (0.25 - fmin) / 2 + fmin
        f_end = fmax
        m = (f_end - f_init) / tt

        c = 1 / tt / 10
        prec = 1e-1  # Precision at sample N for the envelope.
        alfa = -np.log(prec * tt / ((tt - c) ** 2)) / tt
        e = np.exp(-alfa * np.arange(tt)) * (
            (np.arange(tt) - c) ** 2 / (np.arange(tt) + 1e-15)
        )
        e[0] = 0
        e /= np.max(e)

        signal = np.zeros(
            N,
        )
        for i in range(1, 6):
            instf1 = np.zeros(
                N,
            )
            instf1[t_init : t_init + tt] = e * fmin * 0.9**i + i * fmin + 0.05
            phase1 = np.cumsum(instf1)
            x1 = (
                0.9 ** (i - 1)
                * np.cos(2 * pi * phase1)
                * rect_window(N, t_init, t_init + tt)
            )
            x1[t_init : t_init + tt] *= sg.windows.tukey(tt, 0.25)
            signal = signal + Signal(x1, instf=instf1)

        t_init += int(1.01 * tt)

        for i in range(1, 6):
            instf1 = np.zeros(
                N,
            )
            instf1[t_init : t_init + tt] = e * fmin * 0.9 + i * fmin + 0.03
            phase1 = np.cumsum(instf1)
            x1 = (
                0.8 ** (i - 1)
                * np.cos(2 * pi * phase1)
                * rect_window(N, t_init, t_init + tt)
            )
            x1[t_init : t_init + tt] *= sg.windows.tukey(tt, 0.5)
            signal = signal + Signal(x1, instf=instf1)

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_on_off_tones(self):
        """Generates a multicomponent signal comprising components that "born" and "die"
        at different times.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        chirp1 = self._signal_linear_chirp(a=0, b=0.10, instfreq=False)
        chirp2a = self._signal_linear_chirp(a=0, b=0.20, instfreq=False)
        chirp2b = self._signal_linear_chirp(a=0, b=0.20, instfreq=False)
        chirp3 = self._signal_linear_chirp(a=0, b=0.30, instfreq=False)

        Nsub = self.N
        N3 = Nsub // 3
        N4 = Nsub // 4
        N7 = Nsub // 7
        N9 = Nsub // 9

        chirp1[0 : 2 * N7] = 0
        chirp1.comps[0][0 : 2 * N7] = 0
        chirp1.instf[0][0 : 2 * N7] = 0

        chirp1[5 * N7 : -1] = 0
        chirp1.comps[0][5 * N7 : -1] = 0
        chirp1.instf[0][5 * N7 : -1] = 0

        chirp1[2 * N7 : 5 * N7] = chirp1[2 * N7 : 5 * N7] * sg.windows.tukey(
            3 * N7, 0.25
        )
        chirp1.comps[0][2 * N7 : 5 * N7] = chirp1[2 * N7 : 5 * N7] * sg.windows.tukey(
            3 * N7, 0.25
        )

        chirp2a[0:N9] = 0
        chirp2a.comps[0][0:N9] = 0
        chirp2a.instf[0][0:N9] = 0
        chirp2a[8 * N9 : -1] = 0
        chirp2a.comps[0][8 * N9 : -1] = 0
        chirp2a.instf[0][8 * N9 : -1] = 0
        chirp2a[4 * N9 : 5 * N9] = 0
        chirp2a.comps[0][4 * N9 : 5 * N9] = 0
        chirp2a.instf[0][4 * N9 : 5 * N9] = 0
        chirp2a[N9 : 4 * N9] = chirp2a[N9 : 4 * N9] * sg.windows.tukey(3 * N9, 0.25)
        chirp2a.comps[0][N9 : 4 * N9] = chirp2a[N9 : 4 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2a._instf[0][5 * N9 : 8 * N9] = 0
        chirp2a.comps[0][5 * N9 : 8 * N9] = 0
        chirp2a[5 * N9 : 8 * N9] = 0

        chirp2b[0:N9] = 0
        chirp2b.comps[0][0:N9] = 0
        chirp2b.instf[0][0:N9] = 0
        chirp2b[8 * N9 : -1] = 0
        chirp2b.comps[0][8 * N9 : -1] = 0
        chirp2b.instf[0][8 * N9 : -1] = 0
        chirp2b[4 * N9 : 5 * N9] = 0
        chirp2b.comps[0][4 * N9 : 5 * N9] = 0
        chirp2b.instf[0][4 * N9 : 5 * N9] = 0
        chirp2b[5 * N9 : 8 * N9] = chirp2b[5 * N9 : 8 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2b.comps[0][5 * N9 : 8 * N9] = chirp2b[5 * N9 : 8 * N9] * sg.windows.tukey(
            3 * N9, 0.25
        )
        chirp2b._instf[0][N9 : 4 * N9] = 0
        chirp2b.comps[0][N9 : 4 * N9] = 0
        chirp2b[N9 : 4 * N9] = 0

        signal = chirp1 + chirp2b + chirp2a + chirp3

        # TODO: The total number of comps should be generated automatically.
        if not self.return_signal:
            signal = signal.view(np.ndarray)
            # signal.total_ncomps = 4

        return signal

    # Other signals ----------------------------------------------------------------

    def signal_hermite_function(self, order=18, t0=0.5, f0=0.25):
        """Generates a round hermite function of a given order. The spectrogram of
        Hermite functions are given by an annular ridge in the time frequency plane, the
        center of which is given by (t0,f0).

        Args:
            order (int, optional): Order of the Hermite function. Defaults to 18.
            t0 (float, optional): Time coordinate of the center of the spectrogram.
            Defaults to 0.5.
            f0 (float, optional): Frequency coordinate of the center of the spectrogram.
            Defaults to 0.25.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        t0 = int(N * t0)
        t = np.arange(N) - t0
        signal = hermite_fun(N, order, t=t, T=np.sqrt(2 * N)) * np.cos(2 * pi * f0 * t)

        if self.return_signal:
            signal = signal.view(Signal)
            signal._instf = signal[:]

        return signal

    def signal_hermite_elipse(self, order=30, t0=0.5, f0=0.25):
        """Generates a non-round Hermite function of a given order. The spectrogram of
        Hermite functions are given by an elipsoidal ridge in the time frequency plane,
        the center of which is given by (t0,f0).

        Args:
            order (int, optional): Order of the Hermite function. Defaults to 18.
            t0 (float, optional): Time coordinate of the center of the spectrogram.
            Defaults to 0.5.
            f0 (float, optional): Frequency coordinate of the center of the spectrogram.
            Defaults to 0.25.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        t0 = int(N * t0)
        t = np.arange(N) - t0
        signal = hermite_fun(N, order, t=t, T=1.5 * np.sqrt(2 * N)) * np.cos(
            2 * pi * f0 * t
        )

        if self.return_signal:
            signal = signal.view(Signal)
            signal._instf = signal[:]

        return signal

    def signal_mc_triple_impulse(self, Nimpulses=3):
        """Generates three equispaced impulses in time.

        Args:
            Nimpulses (int, optional): Number of impulses. Defaults to 3.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        dloc = Nsub / (Nimpulses + 1)
        signal = np.zeros((N,))
        comps = []

        T = np.sqrt(N)
        t = np.arange(0, N)
        p = 1 / 6
        T2 = T * p
        k = (T2**2 + T**2) / (T * T2) ** 2
        imp_fun = lambda t0: np.exp(-pi / (T2**2) * (t - t0) ** 2) * np.cos(
            2 * pi * 0.25 * (t - t0)
        )

        for i in range(Nimpulses):
            impulse = np.zeros((N,))
            t0 = int((i + 1) * dloc) + tmin
            impulse = imp_fun(t0)
            comps.append(impulse.copy())
            signal += impulse

        if self.return_signal:
            signal = signal.view(Signal)
            signal._comps = comps
            signal._instf = comps

        return signal

    def signal_mc_impulses(self, Nimpulses=5):
        """Generates equispaced impulses in time.

        Args:
            Nimpulses (int, optional): Number of impulses. Defaults to 3.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        dloc = Nsub / (Nimpulses + 1)
        signal = np.zeros((N,))
        comps = []

        T = np.sqrt(N)
        t = np.arange(0, N)
        p = 1 / 6
        T2 = T * p
        k = (T2**2 + T**2) / (T * T2) ** 2
        imp_fun = lambda t0: np.exp(-pi / (T2**2) * (t - t0) ** 2) * np.cos(
            2 * pi * 0.25 * (t - t0)
        )

        for i in range(Nimpulses):
            impulse = np.zeros((N,))
            t0 = int((i + 1) * dloc) + tmin
            impulse = imp_fun(t0) * (i + 1)
            comps.append(impulse.copy())
            signal += impulse

        if self.return_signal:
            signal = signal.view(Signal)
            signal._comps = comps
            signal._instf = comps

        return signal

    def signal_mc_exp_chirps(self):
        """Generates a multicomponent signal comprising three exponential chirps.


        #     Returns:
        #         numpy.ndarray: Returns a numpy array with the signal.
        #"""
        N = self.N
        signal = np.zeros((N,))

        exponents = [4, 3, 2]
        finits = [self.fmin, 1.8 * self.fmin, 2.5 * self.fmin]
        fends = [0.3, 0.8, 1.2]  # [, 0.8]#, 1.2]
        ncomps = len(fends)

        max_freq = self.fmax

        for i in range(ncomps):
            aux = np.zeros((N,))
            _, instf, tmin, tmax = self._signal_exp_chirp(
                finit=finits[i], fend=fends[i], exponent=exponents[i], r_instf=True
            )

            instf2 = instf

            if instf[0] >= max_freq:
                break

            instf[np.where(instf2 > max_freq)] = 0
            instf2 = instf2[np.where(instf2 <= max_freq)]
            tukwin = sg.windows.tukey(len(instf2), 0.5)

            self.check_inst_freq(instf2)
            phase = np.cumsum(instf2)
            x = np.cos(2 * pi * phase)
            tukwin = sg.windows.tukey(len(x), 0.99)

            x = x * tukwin
            aux[tmin : tmin + len(x)] = x

            signal = signal + Signal(aux, instf=instf)

        signal = signal - np.mean(signal)
        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_damped_cos(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        t = np.arange(N) / N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)
        fmax = self.fmax

        signal = np.zeros((N,))
        instf0 = np.zeros_like(signal)
        instf1 = np.zeros_like(signal)
        instf2 = np.zeros_like(signal)

        omega = 5
        f0 = 0.32 + 0.00 * tsub / Nsub
        if0 = f0 + np.exp(np.log(0.25) * tsub / Nsub) * 0.1 * np.cos(
            2 * pi * omega * tsub / Nsub - pi * omega
        )

        if1 = self.fmin + 0.1 * tsub / Nsub
        # if2 = f2+0.02 + 0.02*np.cos(2*pi*omega*tsub/Nsub - pi*omega)
        # if0 = if0[np.where(if0<fmax)]
        # if1 = if1[np.where(if1<fmax)]
        # if2 = if2[np.where(if2<fmax)]

        phase0 = np.cumsum(if0)
        phase1 = np.cumsum(if1)
        # phase2 = np.cumsum(if2)

        x0 = np.zeros_like(signal)
        x1 = np.zeros_like(signal)
        # x2 = np.zeros_like(signal)

        eps = 1e-6
        t = np.arange(Nsub) + eps
        c = 1 / Nsub / 10
        prec = 10e-1  # Precision at sample N for the envelope.
        alfa = -np.log(prec * Nsub / ((Nsub - c) ** 2)) / Nsub
        e = np.exp(-alfa * t) * ((t - c) ** 2 / t)
        e[0] = 0
        e = e / np.max(np.abs(e))

        x0[tmin : tmin + len(phase0)] = np.cos(2 * pi * phase0) * sg.windows.tukey(
            len(phase0), 0.25
        )
        x1[tmin : tmin + len(phase1)] = np.cos(2 * pi * phase1) * sg.windows.tukey(
            len(phase1), 0.25
        )
        # x2[tmin:tmin+len(phase2)] = np.cos(2*pi*phase2)*sg.windows.tukey(len(phase2),0.25)

        instf0[tmin : tmin + len(if0)] = if0
        instf1[tmin : tmin + len(if1)] = if1
        # instf2[tmin:tmin+len(if2)] = if2

        chirp0 = Signal(x0, instf=instf0)
        chirp1 = Signal(x1, instf=instf1)
        # chirp2 = Signal(x2, instf=instf2)

        # signal = x0+x1+x2

        signal = chirp0 + chirp1

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal

    def signal_mc_damped_cos_2(self):
        """Generates a multicomponent signal with different types of components.

        Returns:
            numpy.ndarray: Returns a numpy array with the signal.
        """

        N = self.N
        tmin = self.tmin
        tmax = N - tmin
        Nsub = tmax - tmin
        tsub = np.arange(Nsub)

        signal = np.zeros((N,))
        instf0 = np.zeros_like(signal)
        instf1 = np.zeros_like(signal)

        omega = 5
        f0 = 0.3 + 0.00 * tsub / Nsub
        if0 = f0 + np.exp(np.log(0.25) * tsub / Nsub) * 0.14 * np.cos(
            2 * pi * omega * tsub / Nsub - pi * omega
        )

        if1 = self.fmin + 0.15 * tsub / Nsub

        phase0 = np.cumsum(if0)
        phase1 = np.cumsum(if1)

        x0 = np.zeros_like(signal)
        x1 = np.zeros_like(signal)

        a1 = 0.5 + 0.3 * np.cos(1.3 * pi * omega * tsub / Nsub - pi * omega)

        x0[tmin : tmin + len(phase0)] = np.cos(2 * pi * phase0) * sg.windows.tukey(
            len(phase0), 0.25
        )
        x1[tmin : tmin + len(phase1)] = (
            a1 * np.cos(2 * pi * phase1) * sg.windows.tukey(len(phase1), 0.25)
        )

        instf0[tmin : tmin + len(if0)] = if0
        instf1[tmin : tmin + len(if1)] = if1

        chirp0 = Signal(x0, instf=instf0)
        chirp1 = Signal(x1, instf=instf1)

        signal = chirp0 + chirp1

        if not self.return_signal:
            return signal.view(np.ndarray)
        return signal


def hermite_poly(t, n, return_all=False):
    """Generates a Hermite polynomial of order n on the vector t.

    Args:
        t (ndarray, float): A real valued vector on which compute the Hermite
        polynomials.
        n (int): Order of the Hermite polynomial.

    Returns:
        ndarray: Returns an array with the Hermite polynomial computed on t.
    """

    all_hp = np.zeros((n + 1, len(t)))

    if n == 0:
        hp = np.ones((len(t),))
        all_hp[0] = hp

    else:
        hp = 2 * t
        all_hp[0, :] = np.ones((len(t),))
        all_hp[1, :] = hp
        # if n >= 1:
        for i in range(2, n + 1):
            # hp = 2*t*hermite_poly(t,n-1) - 2*(n-1)*hermite_poly(t,n-2)
            hp = 2 * t * all_hp[i - 1] - 2 * (i - 1) * all_hp[i - 2]
            all_hp[i, :] = hp

    if not return_all:
        return hp
    else:
        return hp, all_hp


def hermite_fun(N, q, t=None, T=None, return_all=False):
    """Computes an Hermite function of order q, that consist in a centered Hermite
    polynomial multiplied by the squared-root of a centered Gaussian given by:
    exp(-pi(t/T)^2). The parameter T fixes the width of the Gaussian function.

    Args:
        N (int): Length of the function in samples
        q (int): Order of the Hermite polynomial.
        t (ndarray): Values on which compute the function. If None, uses a centered
        vector from -N//2 to N//2-1. Defaults to None.
        T (float): Scale of the Gaussian involved in the Hermite function. If None,
        N = sqrt(N). Defaults to None.

    Returns:
        _type_: _description_
    """

    if t is None:
        t = np.arange(N) - N // 2

    if T is None:
        T = np.sqrt(N)

    _, all_hp = hermite_poly(np.sqrt(2 * pi) * t / T, q - 1, return_all=True)
    gaussian_basic = np.exp(-pi * (t / T) ** 2) / np.sqrt(T)
    hfunc = np.zeros((q, len(t)))

    for i in range(q):
        Cnorm = np.sqrt(factorial(q - 1) * (2 ** (q - 1 - 0.5)))
        # gaussian_basic /= np.sum(gaussian_basic)
        hfunc[i] = gaussian_basic * all_hp[i] / Cnorm

    if not return_all:
        return hfunc[-1]
    else:
        return hfunc[-1], hfunc
