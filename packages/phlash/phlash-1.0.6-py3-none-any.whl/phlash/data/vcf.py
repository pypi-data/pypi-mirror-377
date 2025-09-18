"""Methods for working with VCF data (in VCF-Zarr format).

VCFs are expected to be in [VCF Zarr](https://github.com/sgkit-dev/vcf-zarr-spec/blob/main/vcf_zarr_spec.md) format,
as created e.g. using [bio2zarr](https://sgkit-dev.github.io/bio2zarr/intro.html).
"""

import numpy as np
from beartype import beartype
import tskit
from plum import dispatch
import sgkit
import xarray
from collections import defaultdict, Counter
from typing import Any, Sequence
from loguru import logger

import phlash.base as base
import phlash.likelihood as lik
from phlash.util import normalize_sample_ids

def _check_zarr(dataset):
    # check that it has a variable called "populations" with dimensions "samples"
    if 'populations' not in dataset:
        raise ValueError("Zarr dataset must contain a 'populations' variable to "
                         "stratify by population.")
    if dataset.populations.dims != ('samples',):
        raise ValueError("Zarr dataset 'populations' variable must have dimensions "
                         "'samples'.")
    # check that it only has one contig
    if dataset.sizes['contigs'] != 1:
        raise ValueError("Zarr dataset must contain only one contig. Please split your "
                         "data into separate contigs.")

    if dataset.sizes["ploidy"] != 2:
        raise ValueError("Only diploid samples are supported.")


@base.prepare.dispatch
def prepare(model: base.Model, 
            data: xarray.Dataset,
            lik: lik.AfsLikelihood,
            sample_ids: Sequence[str]
            ) -> dict:
    """Precompute auxiliary data for the AFS likelihood from VCF data."""
    _check_zarr(data)

    # normalize sample identifiers
    sample_ids = normalize_sample_ids(sample_ids)

    # check that sample_identifiers are valid
    for s in sample_ids:
        for x in s:
            if x not in data.sample_id:
                raise ValueError(f"Sample identifier {x} not found in VCF data.")

    # check that sample_identifiers are unique
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Sample identifiers must be unique.")

    # subset to samples 
    all_samples = np.array([s for tup in sample_ids for s in tup])
    data = data.sel(samples=np.isin(data.sample_id, all_samples))

    # assign samples to populations
    pd = {}
    for pop, sid in zip(data.populations.values, data.sample_id.values):
        pd.setdefault(pop, []).append(sid)

    # create allele frequency spectrum
    C = sgkit.call_allele_frequencies(data).call_allele_count  # [num_variants, num_samples, num_alleles]
    # to follow tskit, drop multi-allelic sites
    multi = (C[..., 2:] > 0).any(axis=(1, 2)).values  # [num_variants]
    C = C[~multi]
    # tensor that maps [num_samples] to [num_populations] by one-hot encoding
    pops = tuple(pd)
    I = np.eye(len(pops))
    T = np.array([I[pops.index(p)] for p in data.populations])  # [num_pops, num_samples]
    V = np.einsum('vsa,sp->vpa', C, T)  # [num_pops, num_alleles]
    # number of observed non-major allele
    vi = (V.sum(2) - V[..., 0]).astype(int)
    # treat as indices into afs array
    vi = tuple([vi[:, i] for i in range(vi.shape[1])])
    # FIXME assumes diploidy
    afs = np.zeros([1 + 2 * len(v) for v in pd.values()], dtype=np.int64)
    np.add.at(afs, vi, 1)
    return dict(afs=afs, populations=pops)


@base.prepare.dispatch
def prepare(model: base.Model, 
            data: xarray.Dataset,
            lik: lik.SequenceLikelihood,
            sample_ids: Seq) -> dict:
    """Precompute auxiliary data for the Sequence likelihood from VCF data."""
    check_zarr(data)
    # normalize sample identifiers
    samples = normalize_sample_ids(sample_ids)
    # subset to samples 
    all_samples = np.unique([s for tup in samples for s in tup])
    data = data.sel(samples=np.isin(data.container.sample_id, all_samples))

    for s in samples:
        # check that all variants are phased for these two samples
        mask = np.isin(data.sample_id, s)
        if s[0] != s[1] and not data.call_genotype_phased.sel(samples=mask).all():
            raise ValueError(f"Sample identifiers {s} must be phased, i.e. "
                             "call_genotype_phased must be True for these samples.")

    # determine populations 
    pd = dict(zip(data.sample_id.values, data.populations.values))
    pops = []
    for sid in samples:
        pops.append(tuple(map(pd.get, sid)))

    w = lik.window_size
    L = int((data.variant_position.max() - data.variant_position.min()) / w)
    assert w < 2 ** 16
    sidi = list(data.sample_id.values).index
    # create a mapping from sample identifiers to indices
    si0, si1 = map(np.array, zip(*[(sidi(s[0]), sidi(s[1])) for s in samples]))
    # determine index of each variant in the window
    vi = (data.variant_position - data.variant_position.min()) // w
    het = data.call_genotype[:, si0, 0] != data.call_genotype[:, si1, 1]  # [num_variants]
    miss = data.call_genotype_mask[:, si0, 0] | data.call_genotype_mask[:, si1, 1]  # [num_variants]
    vi = vi.compute()
    t_het = (het & ~miss).groupby(vi).sum()
    t_miss = miss.groupby(vi).sum()
    het_matrix = np.stack([w - t_miss, t_het], axis=2)  # [num_windows, 2]
    return dict(het_matrix=het_matrix, populations=pops)


# testing
import stdpopsim 
import sgkit

import pytest

@pytest.fixture
def ts():
    """Create a test tree sequence."""
    spec = stdpopsim.get_species("HomSap")
    contig = spec.get_contig("chr22", length_multiplier=.01)
    model = spec.get_demographic_model("OutOfAfrica_3G09")
    engine = stdpopsim.get_engine("msprime")
    samples = {"YRI": 5, "CHB": 5, "CEU": 5}
    ts = engine.simulate(model, contig, samples, seed=42)
    return ts

@pytest.fixture
def dataset(ts):
    """Create a zarr dataset from the test tree sequence."""
    ts.dump("/tmp/ts.ts")
    import subprocess
    # tskit2zarr convert --force /tmp/ts.ts /tmp/ts.zarr
    subprocess.run(["tskit2zarr", "convert", "--force", "/tmp/ts.ts", "/tmp/ts.zarr"])
    data = sgkit.io.dataset.load_dataset('/tmp/ts.zarr')
    pops = xarray.DataArray(
            data=ts.individual_populations,
            dims=["samples"],
            )
    return data.assign(populations=pops)

def test_vcf_afs(ts, dataset):
    # FIXME change to fixtures
    samples = ["tsk_0", "tsk_1", "tsk_5", "tsk_6", "tsk_10", "tsk_11"]
    data = base.Data[xarray.Dataset, Sequence[str]](container=dataset, samples=samples)
    d = base.prepare(base.Model(), data, lik.AfsLikelihood())
    afs1 = d['afs']
    afs2 = ts.allele_frequency_spectrum(sample_sets=[[0, 1, 2, 3], [10, 11, 12, 13], [20, 21, 22, 23]], span_normalise=False, polarised=True)
    np.testing.assert_allclose(afs1.flat[1:-1], afs2.flat[1:-1])


def test_vcf_seq(dataset):
    data = base.Data[xarray.Dataset, Sequence[str]](container=dataset, samples=["tsk_0", "tsk_1", "tsk_5", "tsk_6", ("tsk_0", "tsk_10")])
    res = base.prepare(base.Model(), data, lik.SequenceLikelihood(window_size=1000))
    np.testing.assert_allclose(res['populations'], 
                               [[0, 0], [0, 0], [1, 1], [1, 1], [0, 2]])

