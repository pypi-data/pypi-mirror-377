from dataclasses import dataclass
from typing import Any
from jaxtyping import Array, Float, PyTree
import phlash.base as base

from phlash.iicr import IICRCurve

@dataclass(kw_only=True)
class Panmictic(base.Model):
    eta: IICRCurve
    mu: float
    r: float

    def iicr(self, pop1: Any, pop2: Any) -> IICRCurve:
        return self.eta

    @classmethod
    def default(
        cls, pattern: str, mu: float, r: float = None, t_max: float = 15.0
    ):
        if r is None:
            r = mu
        # from PSMC. these defaults seem to work pretty well.
        eta = _psmc_size_history(pattern=pattern, alpha=0.1, t_max=t_max)
        return cls(eta=eta, mu=mu, r=r)

    def rescale(self, mu: float) -> "Panmictic":
        """Rescale model so that the mutation rate per unit time is mu.

        Args:
            mu: The mutation rate per locus per generation.

        Returns:
            Rescaled demographic model.
        """
        # the rate of mutation per unit of time in our model is mu/2
        N1_N0 = (self.mu / 2) / mu
        t = N1_N0 * self.eta.t
        c = self.eta.c / N1_N0
        eta = IICRCurve(t=t, c=c)
        r = self.r / N1_N0 if self.rho is not None else None
        return Panmictic(mu=mu, r=r, eta=eta)

    @property
    def M(self):
        return self.eta.M
