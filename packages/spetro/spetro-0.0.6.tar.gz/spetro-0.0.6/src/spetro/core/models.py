from typing import Any, Optional, Tuple, Dict
from abc import ABC, abstractmethod
import numpy as np

from .backends import Backend


class RoughVolatilityModel(ABC):
    @abstractmethod
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        pass


class RoughBergomi(RoughVolatilityModel):
    def __init__(
        self,
        H: float = 0.07,
        eta: float = 1.9,
        rho: float = -0.9,
        xi: float = 0.235**2,
        r: float = 0.0
    ):
        self.H = H
        self.eta = eta
        self.rho = rho
        self.xi = xi
        self.r = r
        
        if not (0 < H < 0.5):
            raise ValueError("hurst parameter must be in (0, 0.5)")
    
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        dt = T / n_steps
        
        if key is None:
            if hasattr(backend, 'random') and hasattr(backend.random, 'PRNGKey'):
                key = backend.random.PRNGKey(42)
            else:
                key = 42
        
        if hasattr(backend, 'random') and hasattr(backend.random, 'split'):
            k1, k2 = backend.random.split(key)
        else:
            k1, k2 = key, key + 1
        
        dW1 = backend.random_normal(k1, (n_paths, n_steps)) * backend.sqrt(dt)
        dW2 = backend.random_normal(k2, (n_paths, n_steps)) * backend.sqrt(dt)
        
        dB = self.rho * dW1 + backend.sqrt(1 - self.rho**2) * dW2
        
        t_grid = backend.array([i * dt for i in range(n_steps + 1)])
        
        Y = self._fractional_brownian_motion(backend, dW1, t_grid, self.H)
        
        V = backend.zeros((n_steps + 1, n_paths))
        if hasattr(V, 'at'):
            V = V.at[0].set(self.xi)
            for i in range(n_steps):
                vol_term = self.xi * backend.exp(self.eta * Y[:, i] - 0.5 * self.eta**2 * t_grid[i+1])
                V = V.at[i+1].set(vol_term)
        else:
            V[0] = self.xi
            for i in range(n_steps):
                vol_term = self.xi * backend.exp(self.eta * Y[:, i] - 0.5 * self.eta**2 * t_grid[i+1])
                V[i+1] = vol_term
        
        log_S = backend.zeros((n_paths, n_steps + 1))
        if hasattr(log_S, 'at'):
            log_S = log_S.at[:, 0].set(backend.log(S0))
        else:
            log_S[:, 0] = backend.log(S0)
        
        for i in range(n_steps):
            vol = backend.sqrt(V[i])
            drift = (self.r - 0.5 * V[i]) * dt
            diffusion = vol * dB[:, i]
            if hasattr(log_S, 'at'):
                log_S = log_S.at[:, i + 1].set(log_S[:, i] + drift + diffusion)
            else:
                log_S[:, i + 1] = log_S[:, i] + drift + diffusion
        
        S = backend.exp(log_S)
        
        return S, V
    
    def _fractional_brownian_motion(
        self, 
        backend: Backend, 
        dW: Any, 
        t_grid: Any, 
        H: float
    ) -> Any:
        n_paths, n_steps = dW.shape
        dt = t_grid[1] - t_grid[0]
        
        g = self._riemann_liouville_kernel(backend, t_grid[1:], H)
        
        if hasattr(backend, 'jnp'):
            g_rev = g[::-1]
            y = backend.jnp.array([backend.jnp.convolve(dW[p], g_rev, mode='valid') 
                                  for p in range(n_paths)])
            return y
        else:
            g_rev = backend.torch.flip(g, dims=[0])
            y = backend.zeros((n_paths, n_steps))
            for p in range(n_paths):
                conv = backend.torch.conv1d(
                    dW[p:p+1].unsqueeze(0), 
                    g_rev.unsqueeze(0).unsqueeze(0), 
                    padding=n_steps-1
                )
                y[p] = conv.squeeze()[:n_steps]
            return y
    
    def _riemann_liouville_kernel(self, backend: Backend, t: Any, H: float) -> Any:
        alpha = H + 0.5
        
        def gamma_func(x):
            if hasattr(backend, 'jax'):
                from jax.scipy.special import gamma
                return gamma(x)
            else:
                return backend.torch.exp(backend.torch.lgamma(backend.array(x)))
        
        normalization = backend.sqrt(2 * H * gamma_func(1.5 - H) / gamma_func(H + 0.5))
        
        kernel = normalization * (t ** (H - 0.5))
        
        return kernel


class RoughHeston(RoughVolatilityModel):
    def __init__(
        self,
        H: float = 0.07,
        nu: float = 0.3,
        theta: float = 0.02,
        rho: float = -0.7,
        V0: float = 0.02,
        r: float = 0.0
    ):
        self.H = H
        self.nu = nu
        self.theta = theta
        self.rho = rho
        self.V0 = V0
        self.r = r
        
        if not (0 < H < 0.5):
            raise ValueError("hurst parameter must be in (0, 0.5)")
    
    def simulate(
        self,
        backend: Backend,
        n_paths: int,
        n_steps: int,
        T: float,
        S0: float,
        key: Optional[Any] = None
    ) -> Tuple[Any, Any]:
        dt = T / n_steps
        
        if key is None:
            if hasattr(backend, 'random') and hasattr(backend.random, 'PRNGKey'):
                key = backend.random.PRNGKey(42)
            else:
                key = 42
        
        if hasattr(backend, 'random') and hasattr(backend.random, 'split'):
            keys = backend.random.split(key, 3)
            k1, k2, k3 = keys[0], keys[1], keys[2]
        else:
            k1, k2, k3 = key, key + 1, key + 2
        
        dW1 = backend.random_normal(k1, (n_paths, n_steps)) * backend.sqrt(dt)
        dW2 = backend.random_normal(k2, (n_paths, n_steps)) * backend.sqrt(dt)
        dZ = backend.random_normal(k3, (n_paths, n_steps)) * backend.sqrt(dt)
        
        dB = self.rho * dW1 + backend.sqrt(1 - self.rho**2) * dW2
        
        V = backend.zeros((n_paths, n_steps + 1))
        S = backend.zeros((n_paths, n_steps + 1))
        
        V = backend.set_item(V, (slice(None), 0), backend.array([self.V0] * n_paths))
        S = backend.set_item(S, (slice(None), 0), backend.array([S0] * n_paths))
        
        for i in range(n_steps):
            v_curr = V[:, i]
            v_sqrt = backend.sqrt(backend.array([max(v, 1e-8) for v in v_curr.flatten()])).reshape(v_curr.shape)
            
            dv = self.theta * dt + self.nu * v_sqrt * dZ[:, i]
            v_next = v_curr + dv
            v_next = backend.array([max(v, 0.0) for v in v_next.flatten()]).reshape(v_next.shape)
            
            V = backend.set_item(V, (slice(None), i + 1), v_next)
            
            drift = self.r * dt
            diffusion = v_sqrt * dB[:, i]
            s_next = S[:, i] * backend.exp(drift - 0.5 * v_curr * dt + diffusion)
            
            S = backend.set_item(S, (slice(None), i + 1), s_next)
        
        return S, V
