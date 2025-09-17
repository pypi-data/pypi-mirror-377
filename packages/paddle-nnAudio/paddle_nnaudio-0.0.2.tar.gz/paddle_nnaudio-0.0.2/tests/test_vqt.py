import pytest
import librosa
import paddle
import sys

sys.path.insert(0, "./")

import os

dir_path = os.path.dirname(os.path.realpath(__file__))

from ppAudio.features import CQT2010v2, VQT
import numpy as np
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
y, sr = librosa.load(librosa.ex('choice'), duration=5)

@pytest.mark.parametrize("device", [*device_args])
def test_vqt_gamma_zero(device):
    paddle.device.set_device(device)
    # qqAudio cqt
    spec = CQT2010v2(sr=sr, verbose=False)
    C2 = spec(paddle.to_tensor(y).unsqueeze(0), output_format="Magnitude", normalization_type='librosa')
    C2 = C2.cpu().numpy().squeeze()

    # qqAudio vqt
    spec = VQT(sr=sr, gamma=0, verbose=False)
    V2 = spec(paddle.to_tensor(y).unsqueeze(0), output_format="Magnitude", normalization_type='librosa')
    V2 = V2.cpu().numpy().squeeze()

    assert (C2 == V2).all() == True


@pytest.mark.parametrize("device", [*device_args])
def test_vqt(device):
    for gamma in [0, 1, 2, 5, 10]:

        # librosa vqt
        V1 = np.abs(librosa.vqt(y, sr=sr, gamma=gamma))

        # nnAudio vqt
        spec = VQT(sr=sr, gamma=gamma, verbose=False)
        V2 = spec(paddle.to_tensor(y).unsqueeze(0), output_format="Magnitude", normalization_type='librosa')
        V2 = V2.cpu().numpy().squeeze()

        # NOTE: there will still be some diff between librosa and nnAudio vqt values (same as cqt)
        # mainly due to the lengths of both - librosa uses float but nnAudio uses int
        # this test aims to keep the diff range within a baseline threshold
        vqt_diff = np.abs(V1 - V2)
        
        assert np.allclose(V1,V2,1e-3,0.8)