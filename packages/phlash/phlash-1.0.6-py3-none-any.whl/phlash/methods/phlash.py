from plum import dispatch

import phlash.base as base
from .params import MCMCParams


# MODEL CLASS
@jax.tree_util.register_dataclass
@dataclass(kw_only=True)
class PhlashModel(MCMCParams):
    c_tr: jax.Array

    @property
    def c(self):
        return jnp.exp(self.c_tr)

    @staticmethod
    def cinv(c: jax.Array) -> jax.Array:
        return jnp.log(c)

    def to_dm(self) -> phlash.size_history.DemographicModel:
        c = self.c
        eta = phlash.size_history.SizeHistory(t=self.times, c=c)
        assert eta.t.shape == eta.c.shape
        return phlash.size_history.DemographicModel(
            eta=eta, theta=self.theta, rho=self.rho
        )

    @classmethod
    def from_linear(
        cls,
        c: jax.Array,
        t1: float,
        tM: float,
        theta: float,
        rho: float,
        N0: float = None,
    ):
        mcp = MCMCParams.from_linear(
            t1=t1,
            tM=tM,
            theta=theta,
            rho=rho,
            N0=N0,
        )

        c_tr = cls.cinv(c)
        return cls(c_tr=c_tr, **asdict(mcp))


# DISPATCH FUNCTIONS
@base.evaluate.dispatch
def evaluate(model: PhlashModel, lik: loglik.afs, data: , aux: Any):
    dm = model.to_dm()
    return phlash.likelihood.psmc(dm, data.hets)

@base.evaluate.dispatch
def evaluate(model: PhlashModel, lik: loglik.arg, data: tskit.TreeSequence, aux: Any):
    dm = model.to_dm()
    return phlash.likelihood.smcprime(dm, data.tmcras)

@base.evaluate.dispatch
def evaluate(model: PhlashModel, data: AFS, aux: Any):
    pass

@base.evaluate.dispatch
def evaluate(model: PhlashModel, data: LDDecay, aux: Any):
    pass


PhlashLikelihood = base.CompositeLikelihood()
