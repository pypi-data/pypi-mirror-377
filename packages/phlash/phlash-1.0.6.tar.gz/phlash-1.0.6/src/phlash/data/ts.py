import jax
import numpy as np
import tskit
from jaxtyping import PyTree
from plum import dispatch
from collections import defaultdict, Sequence

import phlash.base as base
import phlash.likelihood as lik
from phlash.likelihood.afs import PreparedAFS

@base.prepare.dispatch
def prepare(model: base.Model, lik: lik.ArgLikelihood, data: tskit.TreeSequence, sample_ids: Sequence[tuple[int, int]]) -> dict:
    """Precompute auxiliary data for the ARG likelihood of a tree sequence."""
    # loop over the arg, collecting pairwise TMRCA information for each local tree across samples
    tmrcas = defaultdict(list)
    for tree in data.trees():
        for key := (i, j) in sample_ids:
            t = tree.tmrca(i, j)
            a = tmrcas[key]
            if a and a[0] == t:
                a[-1][1] += tree.span
            else:
                a.append([t, tree.span])
    M = max(len(a) for a in tmrcas.values())
    for a in tmrcas.values():
        # pad with missing data to make a square array
        a += [[-1.0, 0.0]] * (M - len(a))
    tmrcas = {k: np.array(v) for k, v in tmrcas.items()}
    populations = _pops_for_sample_ids(data, sample_ids)
    return dict(tmrcas=tmrcas, populations=pops)


@base.prepare.dispatch
def prepare(model: base.Model, data: tskit.TreeSequence, lik: lik.AFSLikelihood, sample_ids: Sequence[int]) -> PreparedAFS:
    """Precompute auxiliary data for the AFS likelihood of a tree sequence."""
    populations = _pops_for_sample_ids(data, sample_ids)
    dd = defaultdict(list)
    for node, pop in zip(sample_ids, populations):
        dd[pop].append(node)
    sample_sets = list(dd.values())
    afs = data.allele_frequency_spectrum(sample_sets, mode="site", span_normalise=False, polarised=True)
    pops = list(dd.keys())
    return dict(afs=afs, populations=pops)


def _pops_for_sample_ids(data: tskit.TreeSequence, sample_ids: PyTree[int, "T"]) -> PyTree[int, "T"]:
    return jax.tree.map(data.individual_populations.__getitem__, sample_ids)
