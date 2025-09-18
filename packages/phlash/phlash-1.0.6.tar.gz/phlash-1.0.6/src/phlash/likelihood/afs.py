"Likelihood of AFS"
import beartype
from plum import dispatch
from typing import Any, TypedDict
import numpy as np

import jax
import jax.numpy as jnp
import momi3
from momi3.jsfs import JSFS
from jaxtyping import Int, Array

import phlash.base as base
import phlash.models as models
from phlash.memory import memory
from phlash.util import normalize_sample_ids

class PreparedAFS(TypedDict):
    afs: Array[Int, "..."]
    populations: Array[Int, "populations"]

class AfsLikelihood(base.Likelihood):
    """Likelihood of AFS (Allele Frequency Spectrum)."""

    @dispatch
    def prepare(self, model: models.Panmictic, prep_data: PreparedAFS):
        assert prep_data['afs'].ndim == 1
        assert np.unique(prep_data['populations'])).size == 1
        n = prep_data['afs'].shape[0] - 1
        W = _W_matrix(n)
        return dict(W=W)


    @dispatch
    def prepare(self, model: models.Demes, prep_data: PreparedAFS):
        n = np.array(prep_data['afs'].shape) - 1
        num_samples = dict(zip(prep_data['populations'], n))
        m3 = momi3.Momi3(model.graph).sfs(num_samples)
        jsfs = momi3.JSFS.from_dense(prep_data['afs'], populations=prep_data['populations'])
        return dict(m3=sfs, jsfs=jsfs)


    @dispatch
    def __call__(self, model: models.Panmictic, prep_data: PreparedAFS, aux: dict) -> float:
        """Calculate the likelihood of the allele frequency spectrum for a single pop."""
        W = aux["W"]
        n = W.shape[0]
        etbl = W @ model.etjj(n)
        esfs = etbl / etbl.sum()
        return jax.scipy.special.xlogy(prepared_data["afs"], esfs).sum()


    @dispatch
    def __call__(self, model: models.Demes, prep_data: PreparedAFS, aux: dict):
        """Calculate the likelihood of the allele frequency spectrum for a demes/multipop model."""
        return aux['m3'].loglik(
            prep_data['afs'], 
            populations=prep_data['populations'].tolist()
        )
        if data.sizes['populations'] > 1:
            return _deme_afs

@memory.cache
def _W_matrix(n: int) -> np.ndarray:
    from fractions import Fraction as mpq  # mimic gmpy2 api

    # IMPORTANT (DO NOT DELETE): this cast makes sure that n is a Python bignum, and not
    # a sneaky np.int64 in disguise. this matters because we need exact integer
    # arithmetic over an unbounded range in the code below.
    n = int(n)
    assert isinstance(n, int)

    # returns W matrix as calculated as eq 13:15 @ Polanski 2013
    # n: sample size
    if n == 1:
        return np.array([[]], dtype=np.float64)
    W = np.zeros(
        [n - 1, n - 1], dtype=object
    )  # indices are [b, j] offset by 1 and 2 respectively
    W[:, 2 - 2] = mpq(6, n + 1)
    if n == 2:
        return W.astype(np.float64)
    b = list(range(1, n))
    W[:, 3 - 2] = np.array([mpq(30 * (n - 2 * bb), (n + 1) * (n + 2)) for bb in b])
    for j in range(2, n - 1):
        A = mpq(-(1 + j) * (3 + 2 * j) * (n - j), j * (2 * j - 1) * (n + j + 1))
        B = np.array([mpq((3 + 2 * j) * (n - 2 * bb), j * (n + j + 1)) for bb in b])
        W[:, j + 2 - 2] = A * W[:, j - 2] + B * W[:, j + 1 - 2]
    return W.astype(np.float64)
