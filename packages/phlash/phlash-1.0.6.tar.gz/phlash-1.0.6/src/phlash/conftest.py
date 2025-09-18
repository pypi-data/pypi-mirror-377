from pytest import fixture
import numpy as np

@fixture
def rng():
    return np.random.default_rng(42)
