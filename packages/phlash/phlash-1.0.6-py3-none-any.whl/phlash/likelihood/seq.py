from dataclasses import dataclass
from jaxtyping import Array, Int
from typing import Any, Sequence
from jax import vmap
import numpy as np
import jax.numpy as jnp

import phlash.models as models
import phlash.base as base
import phlash.hmm as hmm
import phlash.kernel as kernel

from loguru import logger


@dataclass(kw_only=True)
class SequenceLikelihood(base.Likelihood):
    M: int = 16
    warmup_len: int = 500

    def prepare(self, model: base.Model, prep_data: base.PreparedSeqData) -> dict:
        """Precompute any necessary values for the likelihood and data."""
        assert self.warmup_len > 0
        assert self.warmup_len < prep_data.het_matrix.shape[2]
        warmup, hets = np.array_split(prep_data.het_matrix, [self.warmup_len], axis=2)
        kern = kernel.get_kernel(
            M=self.M,
            data=hets,
            double_precision=True,
        )
        return dict(kern=kern, warmup=warmup)

    def __call__(self, model: base.Model, data: base.PreparedSeqData, minibatch: Any, aux: dict) -> float:
        """Evaluate the likelihood for a given model and data."""
        # het matrix dimensions are [samples, chunks, sequence, 2]
        # minibatch is a list of indices into the first two dims of het_matrix
        # if no minibatch, take all of them
        if minibatch is None:
            sh = data.het_matrix.shape
            minibatch = jnp.indices(sh[:2]).reshape(2, -1).T

        # get the populations for each sample.
        pops = data.populations[minibatch[:, 0]]

        @vmap
        def f(pop_pair):
            ii = model.iicr(*pop_pair)
            return kernel.PSMCParams.from_iicr(ii, model.mu, model.r)

        # construct PSMC parameterization for each population pair
        pps = f(pops)

        # "warmup" each chunk by running the forward algorithm for the first `warmup` sequences
        warmup = aux['warmup'][minibatch[:, 0], minibatch[:, 1]]
        pis = vmap(hmm.forward)(pps, warmup)[0]
        pps = pps._replace(pi=pis)
        return kernel.loglik_psmc(pps, minibatch, aux['kern'])


# tests
def test_loglik_seq(seq_data, panmictic_model):
    ll = SequenceLikelihood(M=16, warmup_len=3)
    aux = ll.prepare(panmictic_model, seq_data)
    result = ll(panmictic_model, seq_data, None, aux)
