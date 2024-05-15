import numpy as np

from textboard import resample

def test_resample_one():
    assert resample([1], 1) == [1]

def test_resample_linear():
    assert resample([1, 2], 3) == [1, 1.5, 2]

def test_resample_ndarray():
    assert resample(np.array([1, 2]), 3) == [1, 1.5, 2]