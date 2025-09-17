import pytest
import numpy as np
import librosa
import paddle
from scipy.signal import chirp, sweep_poly
import sys
sys.path.insert(0, './')
from ppAudio.Spectrogram import *
from parameters import *
import warnings


gpu_idx=0 # Choose which GPU to use

# If GPU is avaliable, also test on GPU
if paddle.device.is_compiled_with_cuda():
    device_args = ['cpu', f'gpu:{gpu_idx}']
else:
    warnings.warn("GPU is not avaliable, testing only on CPU")
    device_args = ['cpu']

# librosa example audio for testing
example_y, example_sr = librosa.load(librosa.example('vibeace', hq=False))


@pytest.mark.parametrize("n_fft, win_length", mel_win_parameters)
@pytest.mark.parametrize("device", [*device_args])
def test_mel_spectrogram(n_fft, win_length, device):
    paddle.device.set_device(device)
    x = example_y
    melspec = MelSpectrogram(n_fft=n_fft, win_length=win_length, hop_length=512)
    X = melspec(paddle.to_tensor(x).unsqueeze(0)).squeeze()
    X_librosa = librosa.feature.melspectrogram(x, n_fft=n_fft, win_length=win_length, hop_length=512)
    assert np.allclose(X.cpu(), X_librosa, rtol=1e-3, atol=1e-3)


@pytest.mark.parametrize("device", [*device_args])
def test_mfcc(device):
    paddle.device.set_device(device)
    x = example_y
    mfcc = MFCC(sr=example_sr)
    X = mfcc(paddle.to_tensor(x).unsqueeze(0)).squeeze()
    X_librosa = librosa.feature.mfcc(x, sr=example_sr)
    assert np.allclose(X.cpu(), X_librosa, rtol=1e-3, atol=1e-2)


if paddle.device.is_compiled_with_cuda():
    x = paddle.randn((4,44100)).to(f'gpu:{gpu_idx}') # Create a batch of input for the following Data.Parallel test
    @pytest.mark.parametrize("device", [f'gpu:{gpu_idx}'])
    def test_MelSpectrogram_Parallel(device):
        spec_layer = MelSpectrogram(sr=22050, n_fft=2048, n_mels=128, hop_length=512,
                                                window='hann', center=True, pad_mode='reflect',
                                                power=2.0, htk=False, fmin=0.0, fmax=None, norm=1,
                                                verbose=True)
        spec_layer_parallel = paddle.DataParallel(spec_layer)
        spec = spec_layer_parallel(x)

    @pytest.mark.parametrize("device", [f'gpu:{gpu_idx}'])
    def test_MFCC_Parallel(device):
        paddle.device.set_device(device)
        spec_layer = MFCC()
        spec_layer_parallel = paddle.DataParallel(spec_layer)
        spec = spec_layer_parallel(x)    

def main1():
    paddle.device.set_device("gpu")
    x = example_y
    mfcc = MFCC(sr=example_sr)
    X = mfcc(paddle.to_tensor(x).unsqueeze(0)).squeeze()
    X_librosa = librosa.feature.mfcc(x, sr=example_sr)
    assert np.allclose(X.cpu(), X_librosa, rtol=1e-3, atol=1e-2)

if __name__ == "__main__":
    main()
