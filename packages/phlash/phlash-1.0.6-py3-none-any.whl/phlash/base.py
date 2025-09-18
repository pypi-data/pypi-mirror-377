"""Base classes handling likelihoods, models, and data."""

from plum import dispatch, parametric
from typing import Any, Sequence, TypedDict, TypeVar
from jaxtyping import Array, Int

import jax

from dataclasses import dataclass

T1 = TypeVar("T1")
T2 = TypeVar("T2")

class Model:
    """Base class for models used in inference."""
    def iicr(self, pops: Sequence) -> Callable[[float], tuple[float, float]]:
        pass

# This function is used to precompute any necessary values for the likelihood and data.
# It is specific to each combination of model, data, and likelihood, so
# it doesn't make sense to put it in any particular class. 
# Instead, we rely on multiple dispatch.
@dispatch.abstract
def prepare(model: Model, data: Any, likelihood: Likelihood, sample_ids: Sequence) -> T:
    """Precompute any necessary values for the likelihood and data. Return values can
    be anything, be must be a PyTree with array leaves (i.e. something that can be 
    passed into a jitted function)."""
    pass

# Likelihood objects 
class Likelihood:
    def prepare(self, model: Model, prep_data: Any, sample_ids: Sequence) -> T2:
        """Prepare the likelihood for a given model and data."""
        return

    def __call__(self, model: Model, prep_data: T1, minibatch: None, aux: T2) -> float:
        """Evaluate the likelihood for a given model and data.
        
        Args:
            model: The demographic model.
            prep_data: Precomputed data for the likelihood.
            minibatch: Optional minibatch of data to evaluate the likelihood on.
            aux: Auxiliary data prepared by the prepare method.
        """
        raise NotImplementedError("Likelihood __call__ method must be implemented in subclasses.")

