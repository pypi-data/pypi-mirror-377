import itertools as it
import dask
import dask.bag as db
from beartype import beartype

import phlash.base as base
from phlash.likelihood import AFSLikelihood
from phlash.model import Panmictic


def analyze(cl: base.CompositeLikelihood):
    bag = db.from_sequence(cl, npartitions=1)
    bag = bag.starmap(base.prepare)

# tests
import pytest

def test_analyze():
    from phlash.phlash import PHLASH
    from phlash.ph_demes import PHDemes
    from phlash.ph_eems import PHEEMS

    data = base.Data()
    model = base.Model()
    
    cl = [
        (model, data, PHLASH()),
        (model, data, PHDemes()),
        (model, data, PHEEMS())
    ]

    likelihood_fn = analyze(cl)
    
    assert callable(likelihood_fn)
    assert isinstance(likelihood_fn(model), float)  # Assuming the likelihood returns a float
