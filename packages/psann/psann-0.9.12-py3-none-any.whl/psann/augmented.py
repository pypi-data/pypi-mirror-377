from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import numpy as np
import time
import torch
import torch.nn as nn
import torch.nn.functional as F

from .utils import choose_device, seed_all


def _as_tensor(x, device, dtype=torch.float32):
    if isinstance(x, torch.Tensor):
        return x.to(device=device, dtype=dtype)
    return torch.from_numpy(np.asarray(x, dtype=np.float32)).to(device=device, dtype=dtype)


def _apply_transform(x: torch.Tensor, kind: str, eps: float = 1e-8) -> torch.Tensor:
    k = (kind or "identity").lower()
    if k == "identity":
        return x
    if k == "softmax":
        return torch.softmax(x, dim=-1)
    if k == "tanh":
        return torch.tanh(x)
    if k == "sigmoid":
        return torch.sigmoid(x)
    if k == "relu_norm":
        y = torch.relu(x) + eps
        return y / (y.sum(dim=-1, keepdim=True) + eps)
    raise ValueError(f"Unknown transform '{kind}'")


@dataclass
class PredictiveExtrasConfig:
    episode_length: int
    batch_episodes: int = 16
    primary_dim: int = 1            # first outputs used for reward
    extras_dim: int = 1             # last K outputs predict next extras
    primary_transform: str = "softmax"   # map primary logits -> allocations
    extras_transform: str = "tanh"       # bound extras in (-1,1)
    random_state: Optional[int] = None
    extras_l2: float = 0.0          # regularize extras magnitudes
    extras_smooth: float = 0.0      # regularize changes over time
    trans_cost: float = 0.0         # passed to reward if applicable
    extras_supervision_weight: float = 0.0  # weight for extras reconstruction
    extras_supervision_mode: str = "joint"  # joint | alternate
    extras_supervision_cycle: int = 2           # periods for alternate schedule


class PredictiveExtrasTrainer:
    '''Episode trainer where the model predicts next-step extras.

    The model is assumed to output `primary_dim + extras_dim` values per step:
    - primary: used for reward (e.g., allocation logits, then transformed)
    - extras: transformed to produce next-step extras, concatenated to inputs

    You must provide observed feature episodes X of shape (N, F) and set the
    estimator to accept inputs of shape (F + extras_dim).
    '''

    def __init__(
        self,
        model: nn.Module,
        reward_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor],
        *,
        cfg: PredictiveExtrasConfig,
        device: torch.device | str = "auto",
        lr: float = 1e-3,
        optimizer: Optional[torch.optim.Optimizer] = None,
        grad_clip: Optional[float] = None,
        context_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
        input_noise_std: Optional[float] = None,
        noise_decay: float = 1.0,
        extras_cache: Optional[np.ndarray] = None,
    ) -> None:
        self.model = model
        self.reward_fn = reward_fn
        self.cfg = cfg
        self.device = choose_device(device)
        self.model.to(self.device)
        self.opt = optimizer or torch.optim.Adam(self.model.parameters(), lr=lr)
        self.grad_clip = grad_clip
        self.context_extractor = context_extractor
        seed_all(self.cfg.random_state)
        self.input_noise_std = float(input_noise_std) if input_noise_std is not None else None
        self.noise_decay = float(noise_decay)
        self.history: list[dict] = []
        self._rng = np.random.default_rng(self.cfg.random_state)
        self.extras_cache: Optional[np.ndarray]
        if extras_cache is not None:
            arr = np.asarray(extras_cache, dtype=np.float32)
            if int(self.cfg.extras_dim) > 0 and arr.ndim == 2 and arr.shape[1] == int(self.cfg.extras_dim):
                self.extras_cache = arr.copy()
            elif int(self.cfg.extras_dim) == 0:
                self.extras_cache = None
            else:
                raise ValueError("extras_cache has incompatible shape")
        else:
            self.extras_cache = None

    def _reset_state_if_any(self):
        if hasattr(self.model, "reset_state"):
            self.model.reset_state()

    def _commit_state_if_any(self):
        if hasattr(self.model, "commit_state_updates"):
            self.model.commit_state_updates()

    def _ensure_extras_cache(self, length: int) -> None:
        K = int(self.cfg.extras_dim)
        if K <= 0:
            self.extras_cache = None
            return
        size = max(length + 1, 1)
        if self.extras_cache is None:
            arr = self._rng.normal(0.0, 0.1, size=(size, K)).astype(np.float32)
            arr[0] = 0.0
            self.extras_cache = arr
            return
        if self.extras_cache.shape[1] != K:
            arr = self._rng.normal(0.0, 0.1, size=(size, K)).astype(np.float32)
            arr[0] = 0.0
            self.extras_cache = arr
            return
        if self.extras_cache.shape[0] != size:
            arr = self._rng.normal(0.0, 0.1, size=(size, K)).astype(np.float32)
            arr[0] = 0.0
            n = min(self.extras_cache.shape[0], size)
            arr[:n] = self.extras_cache[:n]
            self.extras_cache = arr

    def _sample_batch(self, X_obs: np.ndarray, epoch_idx: Optional[int] = None) -> tuple[torch.Tensor, np.ndarray]:
        N = X_obs.shape[0]
        T = int(self.cfg.episode_length)
        if N < T:
            raise ValueError(f"Need at least {T} timesteps (got {N})")
        B = int(self.cfg.batch_episodes)
        starts = np.random.randint(0, N - T + 1, size=B)
        batch = np.stack([X_obs[s : s + T] for s in starts], axis=0).astype(np.float32)
        X_ep = _as_tensor(batch, self.device)
        if self.input_noise_std is not None and (self.noise_decay >= 0.0):
            factor = (self.noise_decay ** max(0, (epoch_idx or 0))) if epoch_idx is not None else 1.0
            X_ep = X_ep + torch.randn_like(X_ep) * (self.input_noise_std * factor)
        self._ensure_extras_cache(N)
        return X_ep, starts

    def _rollout(self, X_ep: torch.Tensor, E0: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        '''Rollout over an episode producing primary outputs and extras sequence.

        X_ep: (B,T,F)
        E0:   (B,K) initial extras; if None, zeros

        Returns primary (B,T,P) and extras_seq (B,T+1,K) where extras_seq[:,0]=E0.
        '''
        B, T, F = X_ep.shape
        P = int(self.cfg.primary_dim)
        K = int(self.cfg.extras_dim)
        if K <= 0:
            E0 = torch.zeros((B, 0), device=self.device) if E0 is None else E0
        if E0 is None:
            E0 = torch.zeros((B, K), device=self.device)
        extras_seq = [E0]
        primaries = []
        self._reset_state_if_any()
        for t in range(T):
            xt = torch.cat([X_ep[:, t, :], extras_seq[-1]], dim=-1)
            yt = self.model(xt)
            if yt.ndim == 1:
                yt = yt.unsqueeze(0)
            y_primary = yt[:, :P]
            primaries.append(_apply_transform(y_primary, self.cfg.primary_transform))
            if K > 0:
                y_extras = yt[:, P:P + K]
                next_extras = _apply_transform(y_extras, self.cfg.extras_transform)
            else:
                next_extras = extras_seq[-1]
            extras_seq.append(next_extras)
        primaries_t = torch.stack(primaries, dim=1)
        extras_t = torch.stack(extras_seq, dim=1)
        self._commit_state_if_any()
        return primaries_t, extras_t

    def train(
        self,
        X_obs: np.ndarray,
        *,
        epochs: int = 100,
        verbose: int = 0,
        lr_max: Optional[float] = None,
        lr_min: Optional[float] = None,
    ) -> None:
        X_obs = np.asarray(X_obs, dtype=np.float32)
        if X_obs.ndim != 2:
            raise ValueError("X_obs must be (N, F) for predictive extras training")
        extras_weight = float(getattr(self.cfg, "extras_supervision_weight", 0.0) or 0.0)
        extras_mode = (getattr(self.cfg, "extras_supervision_mode", "joint") or "joint").lower()
        extras_cycle = max(1, int(getattr(self.cfg, "extras_supervision_cycle", 1) or 1))
        if extras_mode not in {"joint", "alternate"}:
            raise ValueError("extras_supervision_mode must be 'joint' or 'alternate'")
        for e in range(epochs):
            if lr_max is not None and lr_min is not None:
                if epochs <= 1:
                    lr_e = float(lr_min)
                else:
                    frac = float(e) / float(max(epochs - 1, 1))
                    lr_e = float(lr_max) + (float(lr_min) - float(lr_max)) * frac
                for g in self.opt.param_groups:
                    g["lr"] = lr_e
            t0 = time.perf_counter()
            X_ep, starts = self._sample_batch(X_obs, epoch_idx=e)
            B, T, F = X_ep.shape
            K = int(self.cfg.extras_dim)
            E0 = None
            if K > 0:
                self._ensure_extras_cache(X_obs.shape[0])
                init = self.extras_cache[starts]
                E0 = torch.from_numpy(init.astype(np.float32)).to(self.device)
                E0.requires_grad_(True)
            primary, extras = self._rollout(X_ep, E0=E0)
            ctx = self.context_extractor(X_ep) if self.context_extractor is not None else X_ep
            rewards = self.reward_fn(primary, ctx)
            loss_reward = -rewards.mean()
            reward_loss_value = float(loss_reward.detach().cpu().item())
            train_reward_value = -reward_loss_value
            extras_sup_loss = None
            extras_sup_value = None
            extras_step = False
            loss = loss_reward
            if K > 0 and extras_weight > 0.0:
                self._ensure_extras_cache(X_obs.shape[0])
                targets_np = np.stack(
                    [self.extras_cache[s + 1 : s + T + 1] for s in starts],
                    axis=0,
                ).astype(np.float32)
                targets_t = torch.from_numpy(targets_np).to(self.device)
                extras_sup_loss = F.mse_loss(extras[:, 1:, :], targets_t)
                extras_sup_value = float(extras_sup_loss.detach().cpu().item())
                if extras_mode == "joint":
                    loss = loss_reward + extras_weight * extras_sup_loss
                else:
                    if extras_cycle <= 1:
                        loss = extras_weight * extras_sup_loss
                        extras_step = True
                    else:
                        step_in_cycle = e % extras_cycle
                        if step_in_cycle == 0:
                            loss = loss_reward
                        else:
                            loss = extras_weight * extras_sup_loss
                            extras_step = True
            if self.cfg.extras_l2 > 0 and self.cfg.extras_dim > 0:
                loss = loss + self.cfg.extras_l2 * extras[:, 1:, :].pow(2).mean()
            if self.cfg.extras_smooth > 0 and self.cfg.extras_dim > 0:
                dE = extras[:, 1:, :] - extras[:, :-1, :]
                loss = loss + self.cfg.extras_smooth * dE.pow(2).mean()

            self.opt.zero_grad()
            loss.backward()
            if self.grad_clip is not None and self.grad_clip > 0:
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.grad_clip)
            self.opt.step()
            with torch.no_grad():
                if K > 0 and self.extras_cache is not None:
                    if E0 is not None and E0.grad is not None:
                        E0 -= 0.1 * E0.grad
                    e0_np = E0.detach().cpu().numpy() if E0 is not None else None
                    if e0_np is not None:
                        self.extras_cache[starts] = e0_np
                    extras_np = extras.detach().cpu().numpy()
                    for b, start in enumerate(starts):
                        end = min(start + extras_np.shape[1], self.extras_cache.shape[0])
                        self.extras_cache[start:end] = extras_np[b, : end - start]
                if E0 is not None:
                    E0.grad = None
            dt = time.perf_counter() - t0
            rec = {
                "epoch": len(self.history) + 1,
                "train_reward": train_reward_value,
                "reward_loss": reward_loss_value,
                "time_s": float(dt),
            }
            if extras_sup_loss is not None:
                rec["extras_loss"] = extras_sup_value
                rec["loss_phase"] = "joint" if extras_mode == "joint" else ("extras" if extras_step else "reward")
            else:
                rec["loss_phase"] = "reward"
            if lr_max is not None and lr_min is not None:
                rec["lr"] = float(self.opt.param_groups[0].get("lr", 0.0))
            self.history.append(rec)
            if verbose:
                msg = f"[PredictiveExtras] epoch {e+1}/{epochs}"
                if lr_max is not None and lr_min is not None:
                    msg += f" lr={rec['lr']:.6g}"
                msg += f" reward={train_reward_value:.6f}"
                if extras_sup_loss is not None:
                    phase = "joint" if extras_mode == "joint" else ("extras" if extras_step else "reward")
                    msg += f" extras_loss={extras_sup_value:.6f} phase={phase}"
                print(msg)

    @torch.no_grad()
    def infer_series(self, X_obs: np.ndarray, *, E0: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        '''Roll out predictions and extras over the full series.

        Returns (primary, extras) as numpy arrays with shapes (N, P) and (N+1, K).
        '''
        self.model.eval()
        X = _as_tensor(X_obs, self.device)
        if X.ndim != 2:
            raise ValueError("X_obs must be (N, F) for series inference")
        N, _ = X.shape
        P = int(self.cfg.primary_dim)
        K = int(self.cfg.extras_dim)
        self._ensure_extras_cache(N)
        if E0 is not None:
            e0 = _as_tensor(E0, self.device).reshape(1, K)
        elif self.extras_cache is not None and K > 0:
            e0 = torch.from_numpy(self.extras_cache[0:1]).to(self.device)
        else:
            e0 = torch.zeros((1, K), device=self.device)
        prim = []
        extras = [e0[0]]
        self._reset_state_if_any()
        for t in range(N):
            xt = torch.cat([X[t : t + 1], extras[-1].reshape(1, -1)], dim=-1)
            yt = self.model(xt)
            y_primary = yt[:, :P]
            prim.append(_apply_transform(y_primary, self.cfg.primary_transform)[0])
            if K > 0:
                y_extras = yt[:, P:P + K]
                next_E = _apply_transform(y_extras, self.cfg.extras_transform)[0]
            else:
                next_E = extras[-1]
            extras.append(next_E)
        self._commit_state_if_any()
        prim_np = torch.stack(prim, dim=0).cpu().numpy()
        extras_np = torch.stack(extras, dim=0).cpu().numpy()
        if K > 0 and self.extras_cache is not None:
            length = min(self.extras_cache.shape[0], extras_np.shape[0])
            self.extras_cache[:length] = extras_np[:length]
        return prim_np, extras_np

    @torch.no_grad()
    def evaluate_reward(self, X_obs: np.ndarray, *, n_batches: int = 8) -> float:
        self.model.eval()
        vals = []
        for _ in range(n_batches):
            X_ep, starts = self._sample_batch(X_obs)
            B, T, F = X_ep.shape
            K = int(self.cfg.extras_dim)
            if K > 0 and self.extras_cache is not None:
                init = self.extras_cache[starts]
                E0 = torch.from_numpy(init.astype(np.float32)).to(self.device)
            else:
                E0 = None
            primary, extras = self._rollout(X_ep, E0=E0)
            if K > 0 and self.extras_cache is not None:
                extras_np = extras.detach().cpu().numpy()
                for b, start in enumerate(starts):
                    end = min(start + extras_np.shape[1], self.extras_cache.shape[0])
                    self.extras_cache[start:end] = extras_np[b, : end - start]
            ctx = self.context_extractor(X_ep) if self.context_extractor is not None else X_ep
            vals.append(float(self.reward_fn(primary, ctx).mean().item()))
        return float(np.mean(vals))

def make_predictive_extras_trainer_from_estimator(
    est, *, cfg: PredictiveExtrasConfig, reward_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor], device: torch.device | str = "auto", lr: float = 1e-3, context_extractor: Optional[Callable[[torch.Tensor], torch.Tensor]] = None,
) -> PredictiveExtrasTrainer:
    if not hasattr(est, "model_"):
        raise RuntimeError("Estimator not fitted; call fit() first.")
    return PredictiveExtrasTrainer(
        est.model_,
        reward_fn,
        cfg=cfg,
        device=device,
        lr=lr,
        context_extractor=context_extractor,
        extras_cache=getattr(est, "_hisso_extras_cache_", None),
    )
