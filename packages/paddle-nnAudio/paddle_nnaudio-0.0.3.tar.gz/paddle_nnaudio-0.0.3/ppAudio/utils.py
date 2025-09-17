"""
Module containing helper functions such as overlap sum and Fourier kernels generators
适配 PaddlePaddle 版本
"""
import sys
import paddle
import paddle.nn.functional as F
from paddle.nn.functional import conv1d, fold
import numpy as np
from time import time
import math
from scipy.signal import get_window
from scipy import signal
from scipy.fftpack import fft
import warnings

import collections
from itertools import repeat
from typing import Any

# 从原代码中保留的 librosa 相关函数（无需修改）
from ppAudio.librosa_functions import *

sz_float = 4  # 浮点数大小
epsilon = 1e-8  # 归一化用的修正因子

# 检查 PaddlePaddle 版本是否支持 fft
__PADDLE_GTE_2_4 = False
split_version = paddle.__version__.split(".")
major_version = int(split_version[0])
minor_version = int(split_version[1])
if major_version > 2 or (major_version == 2 and minor_version >= 4):
    __PADDLE_GTE_2_4 = True
else:
    raise RuntimeError("PaddlePaddle version >= 2.4.0 is required for fft support")


def _ntuple(n, name="parse"):
    def parse(x):
        if isinstance(x, collections.abc.Iterable):
            return tuple(x)
        return tuple(repeat(x, n))

    parse.__name__ = name
    return parse


_single = _ntuple(1, "_single")
_pair = _ntuple(2, "_pair")
_triple = _ntuple(3, "_triple")
_quadruple = _ntuple(4, "_quadruple")


class _ReflectionPadNd(paddle.nn.Layer):
    __constants__ = ["padding"]

    def forward(self, input: paddle.Tensor) -> paddle.Tensor:
        return F.pad(input, self.padding, "reflect")

    def extra_repr(self) -> str:
        return f"{self.padding}"


class ReflectionPad1d(_ReflectionPadNd):
    r"""Pads the input tensor using the reflection of the input boundary.

    For `N`-dimensional padding, use :func:`torch.nn.functional.pad()`.

    Args:
        padding (int, tuple): the size of the padding. If is `int`, uses the same
            padding in all boundaries. If a 2-`tuple`, uses
            (:math:`\text{padding\_left}`, :math:`\text{padding\_right}`)
            Note that padding size should be less than the corresponding input dimension.

    Shape:
        - Input: :math:`(C, W_{in})` or :math:`(N, C, W_{in})`.
        - Output: :math:`(C, W_{out})` or :math:`(N, C, W_{out})`, where

          :math:`W_{out} = W_{in} + \text{padding\_left} + \text{padding\_right}`

    Examples::

        >>> m = nn.ReflectionPad1d(2)
        >>> # xdoctest: +IGNORE_WANT("other tests seem to modify printing styles")
        >>> input = torch.arange(8, dtype=torch.float).reshape(1, 2, 4)
        >>> input
        tensor([[[0., 1., 2., 3.],
                 [4., 5., 6., 7.]]])
        >>> m(input)
        tensor([[[2., 1., 0., 1., 2., 3., 2., 1.],
                 [6., 5., 4., 5., 6., 7., 6., 5.]]])
        >>> # using different paddings for different sides
        >>> m = nn.ReflectionPad1d((3, 1))
        >>> m(input)
        tensor([[[3., 2., 1., 0., 1., 2., 3., 2.],
                 [7., 6., 5., 4., 5., 6., 7., 6.]]])
    """

    #padding: tuple[int, int] # python3.7不支持的语法，还是注释掉吧

    def __init__(self, padding) -> None:
        super().__init__()
        self.padding = _pair(padding)

def rfft_fn(x, n=None, onesided=False):
    """Paddle 实现的实数傅里叶变换"""
    if __PADDLE_GTE_2_4:
        y = paddle.fft.fft(x)
        # 转换为实部+虚部的格式 (..., 2)
        return paddle.stack([y.real(), y.imag()], axis=-1)
    else:
        raise RuntimeError("PaddlePaddle version >= 2.4.0 is required")

## --------------------------- 滤波器设计 ---------------------------##
def paddle_window_sumsquare(w, n_frames, stride, n_fft, power=2):
    """Paddle 实现的窗口平方和计算"""
    w_stacks = w.unsqueeze(-1).tile((1, n_frames)).unsqueeze(0)
    # 窗口长度 + 步长*(帧数-1)
    output_len = w_stacks.shape[1] + stride * (w_stacks.shape[2] - 1)
    return fold(
        w_stacks ** power, 
        output_sizes=(1, output_len), 
        kernel_sizes=(1, n_fft), 
        strides=stride
    )


def overlap_add(X, stride):
    n_fft = X.shape[1]
    output_len = n_fft + stride * (X.shape[2] - 1)

    return fold(X, (1, output_len), kernel_sizes=(1, n_fft), strides=stride).flatten(1)


def uniform_distribution(r1, r2, *size, device):
    """Paddle 实现的均匀分布"""
    return (r1 - r2) * paddle.rand(*size, device=device) + r2


def extend_fbins(X):
    """扩展频率 bins 到完整的 FFT 尺寸"""
    X_upper = X[:, 1:-1].flip(1)
    # 虚部是奇函数
    X_upper[:, :, :, 1] = -X_upper[:, :, :, 1]
    return paddle.concat((X[:, :, :], X_upper), 1)


def downsampling_by_n(x, filterKernel, n):
    """任意倍数下采样"""
    padding = int((filterKernel.shape[-1] - 1) // 2)
    x = conv1d(x, filterKernel, stride=(n,), padding=(padding,))
    return x


def downsampling_by_2(x, filterKernel):
    """2倍下采样"""
    return downsampling_by_n(x, filterKernel, 2)


## 基础计算工具 ##
def nextpow2(A):
    """计算大于等于 A 的最小2的幂"""
    return int(np.ceil(np.log2(A)))


def prepow2(A):
    """计算小于等于 A 的最大2的幂"""
    return int(np.floor(np.log2(A)))


def complex_mul(cqt_filter, stft):
    """复数乘法实现（Paddle 不直接支持复数张量时使用）"""
    cqt_filter_real = cqt_filter[0]
    cqt_filter_imag = cqt_filter[1]
    fourier_real = stft[0]
    fourier_imag = stft[1]

    CQT_real = paddle.matmul(cqt_filter_real, fourier_real) - paddle.matmul(
        cqt_filter_imag, fourier_imag
    )
    CQT_imag = paddle.matmul(cqt_filter_real, fourier_imag) + paddle.matmul(
        cqt_filter_imag, fourier_real
    )

    return CQT_real, CQT_imag

def broadcast_dim(x):
    """
    Auto broadcast input so that it can fits into a Conv1d
    """

    if x.dim() == 2:
        x = x[:, None, :]
    elif x.dim() == 1:
        # If nn.DataParallel is used, this broadcast doesn't work
        x = x[None, None, :]
    elif x.dim() == 3:
        pass
    else:
        raise ValueError(
            "Only support input with shape = (batch, len) or shape = (len)"
        )
    return x


def broadcast_dim_conv2d(x):
    """
    Auto broadcast input so that it can fits into a Conv2d
    """

    if x.dim() == 3:
        x = x[:, None, :, :]

    else:
        raise ValueError(
            "Only support input with shape = (batch, len) or shape = (len)"
        )
    return x


## Kernal generation functions ##
def create_fourier_kernels(
    n_fft,
    win_length=None,
    freq_bins=None,
    fmin=50,
    fmax=6000,
    sr=44100,
    freq_scale="linear",
    window="hann",
    verbose=True,
):
    """This function creates the Fourier Kernel for STFT, Melspectrogram and CQT.
    Most of the parameters follow librosa conventions. Part of the code comes from
    pytorch_musicnet. https://github.com/jthickstun/pytorch_musicnet

    Parameters
    ----------
    n_fft : int
        The window size

    freq_bins : int
        Number of frequency bins. Default is ``None``, which means ``n_fft//2+1`` bins

    fmin : int
        The starting frequency for the lowest frequency bin.
        If freq_scale is ``no``, this argument does nothing.

    fmax : int
        The ending frequency for the highest frequency bin.
        If freq_scale is ``no``, this argument does nothing.

    sr : int
        The sampling rate for the input audio. It is used to calculate the correct ``fmin`` and ``fmax``.
        Setting the correct sampling rate is very important for calculating the correct frequency.

    freq_scale: 'linear', 'log', 'log2', or 'no'
        Determine the spacing between each frequency bin.
        When 'linear', 'log' or 'log2' is used, the bin spacing can be controlled by ``fmin`` and ``fmax``.
        If 'no' is used, the bin will start at 0Hz and end at Nyquist frequency with linear spacing.

    Returns
    -------
    wsin : numpy.array
        Imaginary Fourier Kernel with the shape ``(freq_bins, 1, n_fft)``

    wcos : numpy.array
        Real Fourier Kernel with the shape ``(freq_bins, 1, n_fft)``

    bins2freq : list
        Mapping each frequency bin to frequency in Hz.

    binslist : list
        The normalized frequency ``k`` in digital domain.
        This ``k`` is in the Discrete Fourier Transform equation $$

    """

    if freq_bins == None:
        freq_bins = n_fft // 2 + 1
    if win_length == None:
        win_length = n_fft

    s = np.arange(0, n_fft, 1.0)
    wsin = np.empty((freq_bins, 1, n_fft))
    wcos = np.empty((freq_bins, 1, n_fft))
    start_freq = fmin
    end_freq = fmax
    bins2freq = []
    binslist = []

    # num_cycles = start_freq*d/44000.
    # scaling_ind = np.log(end_freq/start_freq)/k

    # Choosing window shape

    window_mask = get_window(window, int(win_length), fftbins=True)
    window_mask = pad_center(window_mask, n_fft)

    if freq_scale == "linear":
        if verbose == True:
            print(
                f"sampling rate = {sr}. Please make sure the sampling rate is correct in order to"
                f"get a valid freq range"
            )
        start_bin = start_freq * n_fft / sr
        scaling_ind = (end_freq - start_freq) * (n_fft / sr) / freq_bins

        for k in range(freq_bins):  # Only half of the bins contain useful info
            # print("linear freq = {}".format((k*scaling_ind+start_bin)*sr/n_fft))
            bins2freq.append((k * scaling_ind + start_bin) * sr / n_fft)
            binslist.append((k * scaling_ind + start_bin))
            wsin[k, 0, :] = np.sin(
                2 * np.pi * (k * scaling_ind + start_bin) * s / n_fft
            )
            wcos[k, 0, :] = np.cos(
                2 * np.pi * (k * scaling_ind + start_bin) * s / n_fft
            )

    elif freq_scale == "log":
        if verbose == True:
            print(
                f"sampling rate = {sr}. Please make sure the sampling rate is correct in order to"
                f"get a valid freq range"
            )
        start_bin = start_freq * n_fft / sr
        scaling_ind = np.log(end_freq / start_freq) / freq_bins

        for k in range(freq_bins):  # Only half of the bins contain useful info
            # print("log freq = {}".format(np.exp(k*scaling_ind)*start_bin*sr/n_fft))
            bins2freq.append(np.exp(k * scaling_ind) * start_bin * sr / n_fft)
            binslist.append((np.exp(k * scaling_ind) * start_bin))
            wsin[k, 0, :] = np.sin(
                2 * np.pi * (np.exp(k * scaling_ind) * start_bin) * s / n_fft
            )
            wcos[k, 0, :] = np.cos(
                2 * np.pi * (np.exp(k * scaling_ind) * start_bin) * s / n_fft
            )

    elif freq_scale == "log2":
        if verbose == True:
            print(
                f"sampling rate = {sr}. Please make sure the sampling rate is correct in order to"
                f"get a valid freq range"
            )
        start_bin = start_freq * n_fft / sr
        scaling_ind = np.log2(end_freq / start_freq) / freq_bins

        for k in range(freq_bins):  # Only half of the bins contain useful info
            # print("log freq = {}".format(np.exp(k*scaling_ind)*start_bin*sr/n_fft))
            bins2freq.append(2**(k * scaling_ind) * start_bin * sr / n_fft)
            binslist.append((2**(k * scaling_ind) * start_bin))
            wsin[k, 0, :] = np.sin(
                2 * np.pi * (2**(k * scaling_ind) * start_bin) * s / n_fft
            )
            wcos[k, 0, :] = np.cos(
                2 * np.pi * (2**(k * scaling_ind) * start_bin) * s / n_fft
            )

    elif freq_scale == "no":
        for k in range(freq_bins):  # Only half of the bins contain useful info
            bins2freq.append(k * sr / n_fft)
            binslist.append(k)
            wsin[k, 0, :] = np.sin(2 * np.pi * k * s / n_fft)
            wcos[k, 0, :] = np.cos(2 * np.pi * k * s / n_fft)
    else:
        print("Please select the correct frequency scale, 'linear' or 'log'")
    return (
        wsin.astype(np.float32),
        wcos.astype(np.float32),
        bins2freq,
        binslist,
        window_mask.astype(np.float32),
    )


# Tools for CQT


def create_cqt_kernels(
    Q,
    fs,
    fmin,
    n_bins=84,
    bins_per_octave=12,
    norm=1,
    window="hann",
    fmax=None,
    topbin_check=True,
    gamma=0,
    pad_fft=True
):
    """
    Automatically create CQT kernels in time domain
    """

    fftLen = 2 ** nextpow2(np.ceil(Q * fs / fmin))
    # minWin = 2**nextpow2(np.ceil(Q * fs / fmax))

    if (fmax != None) and (n_bins == None):
        n_bins = np.ceil(
            bins_per_octave * np.log2(fmax / fmin)
        )  # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.double(bins_per_octave))

    elif (fmax == None) and (n_bins != None):
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.double(bins_per_octave))

    else:
        warnings.warn("If fmax is given, n_bins will be ignored", SyntaxWarning)
        n_bins = np.ceil(
            bins_per_octave * np.log2(fmax / fmin)
        )  # Calculate the number of bins
        freqs = fmin * 2.0 ** (np.r_[0:n_bins] / np.double(bins_per_octave))

    if np.max(freqs) > fs / 2 and topbin_check == True:
        raise ValueError(
            "The top bin {}Hz has exceeded the Nyquist frequency, \
                          please reduce the n_bins".format(
                np.max(freqs)
            )
        )

    alpha = 2.0 ** (1.0 / bins_per_octave) - 1.0
    lengths = np.ceil(Q * fs / (freqs + gamma / alpha))
    
    # get max window length depending on gamma value
    max_len = int(max(lengths))
    fftLen = int(2 ** (np.ceil(np.log2(max_len))))

    tempKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)
    specKernel = np.zeros((int(n_bins), int(fftLen)), dtype=np.complex64)

    for k in range(0, int(n_bins)):
        freq = freqs[k]
        l = lengths[k]

        # Centering the kernels
        if l % 2 == 1:  # pad more zeros on RHS
            start = int(np.ceil(fftLen / 2.0 - l / 2.0)) - 1
        else:
            start = int(np.ceil(fftLen / 2.0 - l / 2.0))

        window_dispatch = get_window_dispatch(window, int(l), fftbins=True)
        sig = window_dispatch * np.exp(np.r_[-l // 2 : l // 2] * 1j * 2 * np.pi * freq / fs) / l

        if norm:  # Normalizing the filter # Trying to normalize like librosa
            tempKernel[k, start : start + int(l)] = sig / np.linalg.norm(sig, norm)
        else:
            tempKernel[k, start : start + int(l)] = sig
        # specKernel[k, :] = fft(tempKernel[k])

    # return specKernel[:,:fftLen//2+1], fftLen, torch.tensor(lenghts).float()
    return tempKernel, fftLen, paddle.to_tensor(lengths).astype(paddle.float32), freqs


def get_window_dispatch(window, N, fftbins=True):
    if isinstance(window, str):
        return get_window(window, N, fftbins=fftbins)
    elif isinstance(window, tuple):
        if window[0] == "gaussian":
            assert window[1] >= 0
            sigma = np.floor(-N / 2 / np.sqrt(-2 * np.log(10 ** (-window[1] / 20))))
            return get_window(("gaussian", sigma), N, fftbins=fftbins)
        else:
            Warning("Tuple windows may have undesired behaviour regarding Q factor")
    elif isinstance(window, float):
        Warning(
            "You are using Kaiser window with beta factor "
            + str(window)
            + ". Correct behaviour not checked."
        )
    else:
        raise Exception(
            "The function get_window from scipy only supports strings, tuples and floats."
        )


def get_cqt_complex(x, cqt_kernels_real, cqt_kernels_imag, hop_length, padding):
    """
    与STFT结果乘以cqt_kernel，参考1992年的CQT论文[1]
    关于如何将STFT结果与CQT核相乘的方法
    [2] Brown, Judith C.C. and Miller Puckette. “An efficient algorithm for the calculation of
    a constant Q transform.” (1992).
    """
    # STFT，将音频输入从时域转换到频域
    try:
        x = padding(x)  # 当center == True时，需要在开头和结尾进行填充
    except:
        warnings.warn(
            f"\n输入大小 = {x.shape}\t核大小 = {cqt_kernels_real.shape[-1]}\n"
            "反射模式的填充可能不是最佳选择，请尝试使用常数填充",
            UserWarning,
        )

        pad_size = cqt_kernels_real.shape[-1] // 2
        x = paddle.nn.functional.pad(
            x, (pad_size, pad_size), data_format="NCL"
        )
    
    # 计算实部和虚部的卷积
    CQT_real = paddle.nn.functional.conv1d(x, cqt_kernels_real, stride=hop_length)
    CQT_imag = -paddle.nn.functional.conv1d(x, cqt_kernels_imag, stride=hop_length)
    
    # 堆叠实部和虚部作为复数结果
    return paddle.stack((CQT_real, CQT_imag), axis=-1)


def get_cqt_complex2(
    x, cqt_kernels_real, cqt_kernels_imag, hop_length, padding, wcos=None, wsin=None
):
    """Multiplying the STFT result with the cqt_kernel, check out the 1992 CQT paper [1]
    for how to multiple the STFT result with the CQT kernel
    [2] Brown, Judith C.C. and Miller Puckette. “An efficient algorithm for the calculation of
    a constant Q transform.” (1992)."""

    # STFT, converting the audio input from time domain to frequency domain
    try:
        x = padding(
            x
        )  # When center == True, we need padding at the beginning and ending
    except:
        warnings.warn(
            f"\ninput size = {x.shape}\tkernel size = {cqt_kernels_real.shape[-1]}\n"
            "padding with reflection mode might not be the best choice, try using constant padding",
            UserWarning,
        )
        x = paddle.nn.functional.pad(
            x, (cqt_kernels_real.shape[-1] // 2, cqt_kernels_real.shape[-1] // 2), data_format="NCL"
        )

    if wcos is None or wsin is None:
        CQT_real = conv1d(x, cqt_kernels_real, stride=hop_length)
        CQT_imag = -conv1d(x, cqt_kernels_imag, stride=hop_length)

    else:
        fourier_real = conv1d(x, wcos, stride=hop_length)
        fourier_imag = conv1d(x, wsin, stride=hop_length)
        # Multiplying input with the CQT kernel in freq domain
        CQT_real, CQT_imag = complex_mul(
            (cqt_kernels_real, cqt_kernels_imag), (fourier_real, fourier_imag)
        )

    return paddle.stack((CQT_real, CQT_imag), axis = -1)


def create_lowpass_filter(band_center=0.5, kernelLength=256, transitionBandwidth=0.03):
    """
    Calculate the highest frequency we need to preserve and the lowest frequency we allow
    to pass through.
    Note that frequency is on a scale from 0 to 1 where 0 is 0 and 1 is Nyquist frequency of
    the signal BEFORE downsampling.
    """

    # transitionBandwidth = 0.03
    passbandMax = band_center / (1 + transitionBandwidth)
    stopbandMin = band_center * (1 + transitionBandwidth)

    # Unlike the filter tool we used online yesterday, this tool does
    # not allow us to specify how closely the filter matches our
    # specifications. Instead, we specify the length of the kernel.
    # The longer the kernel is, the more precisely it will match.
    # kernelLength = 256

    # We specify a list of key frequencies for which we will require
    # that the filter match a specific output gain.
    # From [0.0 to passbandMax] is the frequency range we want to keep
    # untouched and [stopbandMin, 1.0] is the range we want to remove
    keyFrequencies = [0.0, passbandMax, stopbandMin, 1.0]

    # We specify a list of output gains to correspond to the key
    # frequencies listed above.
    # The first two gains are 1.0 because they correspond to the first
    # two key frequencies. the second two are 0.0 because they
    # correspond to the stopband frequencies
    gainAtKeyFrequencies = [1.0, 1.0, 0.0, 0.0]

    # This command produces the filter kernel coefficients
    filterKernel = signal.firwin2(kernelLength, keyFrequencies, gainAtKeyFrequencies)

    return filterKernel.astype(np.float32)


def get_early_downsample_params(sr, hop_length, fmax_t, Q, n_octaves, verbose):
    """Used in CQT2010 and CQT2010v2"""

    window_bandwidth = 1.5  # for hann window
    filter_cutoff = fmax_t * (1 + 0.5 * window_bandwidth / Q)
    sr, hop_length, downsample_factor = early_downsample(
        sr, hop_length, n_octaves, sr // 2, filter_cutoff
    )
    if downsample_factor != 1:
        if verbose == True:
            print("Can do early downsample, factor = ", downsample_factor)
        earlydownsample = True
        # print("new sr = ", sr)
        # print("new hop_length = ", hop_length)
        early_downsample_filter = create_lowpass_filter(
            band_center=1 / downsample_factor,
            kernelLength=256,
            transitionBandwidth=0.03,
        )
        early_downsample_filter = paddle.to_tensor(early_downsample_filter)[None, None, :]

    else:
        if verbose == True:
            print(
                "No early downsampling is required, downsample_factor = ",
                downsample_factor,
            )
        early_downsample_filter = None
        earlydownsample = False

    return sr, hop_length, downsample_factor, early_downsample_filter, earlydownsample


def early_downsample(sr, hop_length, n_octaves, nyquist, filter_cutoff):
    """Return new sampling rate and hop length after early dowansampling"""
    downsample_count = early_downsample_count(
        nyquist, filter_cutoff, hop_length, n_octaves
    )
    # print("downsample_count = ", downsample_count)
    downsample_factor = 2 ** (downsample_count)

    hop_length //= downsample_factor  # Getting new hop_length
    new_sr = sr / float(downsample_factor)  # Getting new sampling rate
    sr = new_sr

    return sr, hop_length, downsample_factor


# The following two downsampling count functions are obtained from librosa CQT
# They are used to determine the number of pre resamplings if the starting and ending frequency
# are both in low frequency regions.
def early_downsample_count(nyquist, filter_cutoff, hop_length, n_octaves):
    """Compute the number of early downsampling operations"""

    downsample_count1 = max(
        0, int(np.ceil(np.log2(0.85 * nyquist / filter_cutoff)) - 1) - 1
    )
    # print("downsample_count1 = ", downsample_count1)
    num_twos = nextpow2(hop_length)
    downsample_count2 = max(0, num_twos - n_octaves + 1)
    # print("downsample_count2 = ",downsample_count2)

    return min(downsample_count1, downsample_count2)


def early_downsample(sr, hop_length, n_octaves, nyquist, filter_cutoff):
    """Return new sampling rate and hop length after early dowansampling"""
    downsample_count = early_downsample_count(
        nyquist, filter_cutoff, hop_length, n_octaves
    )
    # print("downsample_count = ", downsample_count)
    downsample_factor = 2 ** (downsample_count)

    hop_length //= downsample_factor  # Getting new hop_length
    new_sr = sr / float(downsample_factor)  # Getting new sampling rate

    sr = new_sr

    return sr, hop_length, downsample_factor
