"Sparse variational gaussian process"

from dataclasses import dataclass, replace, field

import equinox as eqx
import jax
import jax.numpy as jnp
import numpy as np
import optax
import scipy
from jax import jit, value_and_grad, vmap
from typing import Callable, NamedTuple

import phlash.ld.stats


def e_log_p(y, mu, sigma2, tau2):
    "expectation of log p(y|f) when f ~ N(mu, sigma2) and y ~ N(f, tau2)"
    return -0.5 * (jnp.log(2 * jnp.pi * tau2) + ((y - mu) ** 2 + sigma2) / tau2)


def rbf_kern(x, y, alpha, sigma2):
    # x = eqx.debug.backward_nan(x, name="x")
    # y = eqx.debug.backward_nan(y, name="y")
    # alpha = eqx.debug.backward_nan(alpha, name="alpha")
    # sigma2 = eqx.debug.backward_nan(sigma2, name="sigma2")
    e = x - y
    return sigma2 * jnp.exp(-alpha * jnp.sum(e * e, axis=-1))


class NormReparam(NamedTuple):
    m_tilde: jax.Array
    S_tilde_sp: jax.Array

    @property
    def S_tilde(self):
        return 1e-6 + jax.nn.softplus(self.S_tilde_sp)


@jax.tree_util.register_dataclass
@dataclass
class SVGPParams:
    qU: NormReparam
    tau_x: float
    alpha_x: float
    sigma2_x: float
    Z: jax.Array

    _kernel: Callable = field(default=rbf_kern, metadata=dict(static=True))

    @property
    def M(self):
        return self.Z.shape[0]

    @property
    def tau(self):
        return jax.nn.softplus(self.tau_x)

    @property
    def alpha(self):
        return jax.nn.softplus(self.alpha_x)

    @property
    def sigma2(self):
        return jax.nn.softplus(self.sigma2_x)

    def kernel(self, x, y):
        return self._kernel(x, y, self.alpha, self.sigma2)

    def K_uu(self):
        return self.kernel(self.Z[:, None], self.Z[None, :])

    def q_test(self, X_test):
        """
        Computes mean and covariance of latent function values at test inputs X_test.
        """
        # (f_test, u) ~ N(0, K)
        # f_test | u ~ N(K_su @ K_uu^-1 @ u, K_ss - K_su @ K_uu^-1 @ K_us)
        # by law of total covariance, cov(f_test) = E(cov(f_test | u)) + cov(E(f_test | u))
        # E(cov(f_test) | u) = K_ss - K_su @ K_uu^-1 @ K_us
        # if u ~ N(m, S) then
        # E(f_test | u) = K_su @ K_uu^-1 @ u
        # E(u u^T | u) = S + m m^T
        # cov(E(f_test | u)) = cov(K_su @ K_uu^-1 @ u) = K_su @ K_uu^-1 @ S @ K_uu^-1 @ K_us
        # thus cov(f_test) = K_ss - K_su @ K_uu^-1 @ K_us + K_su @ K_uu^-1 @ S @ K_uu^-1 @ K_us
        # = K_ss - K_su @ (K_uu^-1 - K_uu^-1 S @ K_uu^-1) @ K_us
        # Now S = (K_uu^-1 + diag(S_tilde)^-1)^-1 so
        # K_uu^-1 - K_uu^-1 S @ K_uu^-1 = K_uu^-1 - K_uu^-1 (K_uu^-1 + diag(S_tilde)^-1)^-1 @ K_uu^-1
        # = K_uu^-1 - (K_uu + K_uu diag(S_tilde)^-1 K_uu)^-1
        # A^-1 - B^-1 = (B - A)^-1 B A^-1
        K_ss = self.kernel(X_test[:, None], X_test[None, :])
        K_su = self.kernel(X_test[:, None], self.Z[None, :])
        K_us = K_su.T
        K_uu = self.K_uu()
        # S = (K_uu^-1 + diag(S_tilde)^-1)^-1
        # K_uu^-1 @ S @ K_uu^-1 = (I + K_uu diag(S_tilde)^-1 K_uu)^-1
        mu = K_su @ jnp.linalg.solve(
            self.K_uu() + jnp.diag(self.qU.S_tilde), self.qU.m_tilde
        )
        cov = K_ss
        cov -= K_su @ jnp.linalg.solve(K_uu, K_us)
        cov += K_su @ jnp.linalg.solve(
            K_uu + K_uu @ jnp.diag(1 / self.qU.S_tilde) @ K_uu, K_us
        )
        return mu, cov


def neg_elbo(phi: SVGPParams, y, X):
    K_tilde_cho = jax.scipy.linalg.cho_factor(phi.K_uu() + jnp.diag(phi.qU.S_tilde))

    def K_tilde_inv(v):
        return jax.scipy.linalg.cho_solve(K_tilde_cho, v)

    u_tilde = K_tilde_inv(phi.qU.m_tilde)
    Knu = phi.kernel(X[:, None], phi.Z[None, :])
    mu_tilde = Knu @ u_tilde
    sigma2 = phi.sigma2 - Knu @ K_tilde_inv(Knu.T)

    ll = vmap(e_log_p, (0, 0, 0, None))(y, mu_tilde, sigma2, phi.tau**2)
    N = len(ll)

    kl = 0.5 * (
        -jnp.trace(K_tilde_inv(jnp.diag(phi.qU.S_tilde)))
        + u_tilde.T @ phi.K_uu() @ u_tilde
        - phi.M
        + 2 * jnp.log(jnp.diag(K_tilde_cho[0])).sum()  # log |K_tilde|
        - jnp.log(phi.qU.S_tilde).sum()  # log |S_tilde|
    )

    return -(ll.mean() - kl / N)


def predict(y_star, X_star, phi):
    "predictive density p(y*|X*, phi)"
    K_tilde_cho = jax.scipy.linalg.cho_factor(phi.K_uu() + jnp.diag(phi.qU.S_tilde))


def train(phi, y, X, n_iter=1000, lr=1e-3):
    opt = optax.adam(lr)
    opt_state = opt.init(phi)
    obj = jit(value_and_grad(neg_elbo))
    for _ in range(n_iter):
        loss, grads = obj(phi, y, X)
        updates, opt_state = opt.update(grads, opt_state)
        # don't learn inducing point locations, for now
        # updates = replace(updates, Z=None)
        phi = eqx.apply_updates(phi, updates)
        print(loss)
    return phi


def data_iter(
    physical_pos, genetic_pos, genotypes, rng, batch_size=1_000, min_g=1e-4, max_g=0.2
):
    assert genotypes.ndim == 3
    assert genotypes.shape[2] == 2
    assert len(physical_pos) == len(genotypes)
    assert len(genetic_pos) == len(physical_pos)
    assert physical_pos.ndim == 1
    assert genetic_pos.ndim == 1
    nmiss = (genotypes != -1).all((1, 2))
    biallelic = (genotypes.max((1, 2)) == 1) & (genotypes.min((1, 2)) == 0)
    mask = nmiss & biallelic
    genotypes = jnp.array(genotypes[mask])
    genetic_pos = jnp.array(genetic_pos[mask])
    physical_pos = jnp.array(physical_pos[mask])

    @jit
    @vmap
    def f(i, j):
        g_x = genotypes[i]
        p_x = genetic_pos[i]
        s_x = 3 * jnp.sum(g_x, 1)
        p_y = genetic_pos[j]
        g_y = genotypes[j]
        r = s_x + jnp.sum(g_y, 1)
        counts = jnp.bincount(r, length=9)
        return jnp.array(
            [
                f(counts)
                for f in [phlash.ld.stats.D2, phlash.ld.stats.Dz, phlash.ld.stats.pi2]
            ]
        )

    while True:
        idx0 = rng.choice(len(genotypes), size=(batch_size,))
        idx1 = idx0 + 100 + rng.geometric(1e-4, size=(batch_size,))
        idx1 = np.minimum(idx1, len(genotypes) - 1)
        idx = np.stack([idx0, idx1], 1)
        g = abs(jnp.diff(genetic_pos[idx], axis=1))[:, 0]
        c = f(idx[:, 0], idx[:, 1])  # [B, 3]
        yield g, c.T


@jit
@value_and_grad
def multi_obj(phis, ys, X):
    return vmap(neg_elbo, (0, 0, None))(phis, ys, X).sum()


def calc_ld(physical_pos, genetic_pos, genotypes, niter=5_000, rng=None, lr=1e-3, M=50):
    # init rng
    if rng is None:
        rng = np.random.default_rng(1)
    di = data_iter(physical_pos, genetic_pos, genotypes, rng)
    # init params
    Z = rng.uniform(-6, 0, size=(M, 1))
    qU = NormReparam(rng.normal(size=(M,)), rng.normal(size=(M,)))
    phis = vmap(lambda _: SVGPParams(qU, 1.0, 1.0, 1.0, Z))(jnp.arange(3))
    # training
    opt = optax.adam(1e-3)
    opt_state = opt.init(phis)
    best_loss = None
    i = 0
    for _ in range(niter):
        X, ys = next(di)  # [B, 1, 1], [B, 3]
        loss, grads = multi_obj(phis, ys, X[..., None])
        updates, opt_state = opt.update(grads, opt_state)
        # don't learn inducing point locations, for now
        # updates = replace(updates, Z=None)
        phis = eqx.apply_updates(phis, updates)
        print(loss)
    return phis
