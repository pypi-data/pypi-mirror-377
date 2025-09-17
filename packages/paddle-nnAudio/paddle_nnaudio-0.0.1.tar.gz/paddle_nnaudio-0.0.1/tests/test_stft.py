import pytest
import librosa
import paddle
from scipy.signal import chirp, sweep_poly
import sys
import numpy as np

sys.path.insert(0, "./")
from ppAudio.Spectrogram import *
from parameters import *
import warnings


gpu_idx = 0  # Choose which GPU to use

# If GPU is avaliable, also test on GPU
if paddle.device.is_compiled_with_cuda():
    device_args = ['cpu', f'gpu:{gpu_idx}']
else:
    warnings.warn("GPU is not avaliable, testing only on CPU")
    device_args = ['cpu']

# librosa example audio for testing
example_y, example_sr = librosa.load(librosa.example('vibeace', hq=False))


@pytest.mark.parametrize("n_fft, hop_length, window", stft_parameters)
@pytest.mark.parametrize("device", [*device_args])
def test_inverse2(n_fft, hop_length, window, device):
    paddle.device.set_device(device)
    x = paddle.to_tensor(example_y)
    stft = STFT(n_fft=n_fft, hop_length=hop_length, window=window)
    istft = iSTFT(n_fft=n_fft, hop_length=hop_length, window=window)
    X = stft(x.unsqueeze(0), output_format="Complex")
    x_recon = istft(X, length=x.shape[0], onesided=True).squeeze()
    assert np.allclose(x.cpu(), x_recon.cpu(), rtol=1e-5, atol=1e-3)
    x = paddle.randn([4, 16000])
    X = stft(x, output_format="Complex")
    x_recon = istft(X, length=x.shape[1], onesided=True).squeeze()
    assert np.allclose(x.cpu(), x_recon.cpu(), rtol=1e-5, atol=1e-3)


@pytest.mark.parametrize("n_fft, hop_length, window", stft_parameters)
@pytest.mark.parametrize("device", [*device_args])
def test_inverse(n_fft, hop_length, window, device):
    paddle.device.set_device(device)
    x = paddle.to_tensor(example_y)
    stft = STFT(n_fft=n_fft, hop_length=hop_length, window=window, iSTFT=True).to(
        device
    )
    X = stft(x.unsqueeze(0), output_format="Complex")
    x_recon = stft.inverse(X, length=x.shape[0]).squeeze()
    assert np.allclose(x.cpu(), x_recon.cpu(), rtol=1e-3, atol=1)
    x = paddle.randn([4, 16000])
    X = stft(x, output_format="Complex")
    x_recon = stft.inverse(X, length=x.shape[1]).squeeze()
    assert np.allclose(x.cpu(), x_recon.cpu(), rtol=1e-5, atol=1e-3)


@pytest.mark.parametrize("n_fft, hop_length, window", stft_parameters)
@pytest.mark.parametrize("device", [*device_args])
def test_stft_complex(n_fft, hop_length, window, device):
    paddle.device.set_device(device)
    x = example_y
    stft = STFT(n_fft=n_fft, hop_length=hop_length, window=window)
    X = stft(paddle.to_tensor(x).unsqueeze(0), output_format="Complex")
    X_real, X_imag = X[:, :, :, 0].squeeze(), X[:, :, :, 1].squeeze()
    X_librosa = librosa.stft(x, n_fft=n_fft, hop_length=hop_length, window=window)
    real_diff, imag_diff = np.allclose(
        X_real.cpu(), X_librosa.real, rtol=1e-1, atol=1e-1
    ), np.allclose(X_imag.cpu(), X_librosa.imag, rtol=1e-1, atol=1e-1)

    assert real_diff and imag_diff


@pytest.mark.parametrize("n_fft, win_length, hop_length", stft_with_win_parameters)
@pytest.mark.parametrize("device", [*device_args])
def test_stft_complex_winlength(n_fft, win_length, hop_length, device):
    paddle.device.set_device(device)
    x = example_y
    stft = STFT(n_fft=n_fft, win_length=win_length, hop_length=hop_length)
    X = stft(paddle.to_tensor(x).unsqueeze(0), output_format="Complex")
    X_real, X_imag = X[:, :, :, 0].squeeze(), X[:, :, :, 1].squeeze()
    X_librosa = librosa.stft(
        x, n_fft=n_fft, win_length=win_length, hop_length=hop_length
    )
    real_diff, imag_diff = np.allclose(
        X_real.cpu(), X_librosa.real, rtol=1e-3, atol=1e-3
    ), np.allclose(X_imag.cpu(), X_librosa.imag, rtol=1e-3, atol=1e-3)
    assert real_diff and imag_diff


@pytest.mark.parametrize("device", [*device_args])
def test_stft_magnitude(device):
    paddle.device.set_device(device)
    x = example_y
    stft = STFT(n_fft=2048, hop_length=512)
    X = stft(
        paddle.to_tensor(x).unsqueeze(0), output_format="Magnitude"
    ).squeeze()
    X_librosa, _ = librosa.core.magphase(librosa.stft(x, n_fft=2048, hop_length=512))
    assert np.allclose(X.cpu(), X_librosa, rtol=1e-1, atol=1e-1)


@pytest.mark.parametrize("device", [*device_args])
def test_stft_phase(device):
    paddle.device.set_device(device)
    x = example_y
    stft = STFT(n_fft=2048, hop_length=512)
    X = stft(paddle.to_tensor(x).unsqueeze(0), output_format="Phase")
    X_real, X_imag = paddle.cos(X).squeeze(), paddle.sin(X).squeeze()
    _, X_librosa = librosa.core.magphase(librosa.stft(x, n_fft=2048, hop_length=512))

    real_diff, imag_diff = np.mean(
        np.abs(X_real.cpu().numpy() - X_librosa.real)
    ), np.mean(np.abs(X_imag.cpu().numpy() - X_librosa.imag))

    # I find that np.allclose is too strict for allowing phase to be similar to librosa.
    # Hence for phase we use average element-wise distance as the test metric.
    assert real_diff < 2e-2 and imag_diff < 2e-2


if paddle.device.is_compiled_with_cuda():
    paddle.device.set_device("gpu:0")
    x = paddle.randn((4, 44100)) # Create a batch of input for the following Data.Parallel test

    @pytest.mark.parametrize("device", [f"cuda:{gpu_idx}"])
    def test_STFT_Parallel(device):
        spec_layer = STFT(
            hop_length=512,
            n_fft=2048,
            window="hann",
            freq_scale="no",
            output_format="Complex",
        )
        inverse_spec_layer = iSTFT(
            hop_length=512, n_fft=2048, window="hann", freq_scale="no"
        )

        spec_layer_parallel = paddle.DataParallel(spec_layer)
        inverse_spec_layer_parallel = paddle.DataParallel(inverse_spec_layer)
        spec = spec_layer_parallel(x)
        x_recon = inverse_spec_layer_parallel(spec, onesided=True, length=x.shape[-1])

        assert np.allclose(
            x_recon.detach().cpu(), x.detach().cpu(), rtol=1e-3, atol=1e-3
        )

#if __name__ == "__main__":
#    test_inverse2(256, None, "hann", "cpu")