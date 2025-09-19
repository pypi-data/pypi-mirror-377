from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

import numpy as np
import torch


@dataclass
class SupervisedExtrasConfig:
    """Metadata describing supervised extras behaviour for time-series models."""

    primary_dim: int
    extras_dim: int
    feature_dim: int
    append_to_inputs: bool
    weight: float = 1.0
    mode: str = "joint"
    cycle: int = 1

    @property
    def base_dim(self) -> int:
        if self.append_to_inputs:
            return int(self.feature_dim) - int(self.extras_dim)
        return int(self.feature_dim)


def ensure_supervised_extras_config(value: Any) -> SupervisedExtrasConfig:
    """Coerce persisted metadata into :class:`SupervisedExtrasConfig`."""

    if isinstance(value, SupervisedExtrasConfig):
        return value
    if isinstance(value, dict):
        return SupervisedExtrasConfig(
            primary_dim=int(value.get("primary_dim", value.get("primary", 0))),
            extras_dim=int(value.get("extras_dim", value.get("extras", 0))),
            feature_dim=int(value.get("feature_dim", value.get("features", 0))),
            append_to_inputs=bool(value.get("append_to_inputs", value.get("append", False))),
            weight=float(value.get("weight", value.get("extras_loss_weight", 1.0))),
            mode=str(value.get("mode", value.get("extras_loss_mode", "joint"))),
            cycle=int(value.get("cycle", value.get("extras_loss_cycle", 1))),
        )
    raise ValueError("Unsupported supervised extras configuration format")


def _normalise_initial_extras(
    extras_dim: int,
    *,
    initial_extras: Optional[np.ndarray],
    cache: Optional[np.ndarray],
) -> np.ndarray:
    if extras_dim <= 0:
        raise ValueError("extras_dim must be positive for extras rollout")
    if initial_extras is not None:
        arr = np.asarray(initial_extras, dtype=np.float32).reshape(-1)
        if arr.shape[-1] != extras_dim:
            raise ValueError(
                f"initial extras length {arr.shape[-1]} does not match extras_dim={extras_dim}"
            )
        return arr.astype(np.float32, copy=False)
    if cache is not None:
        arr = np.asarray(cache, dtype=np.float32)
        if arr.ndim == 1:
            if arr.shape[0] == extras_dim:
                return arr.astype(np.float32, copy=False)
        elif arr.ndim == 2 and arr.shape[1] == extras_dim:
            return arr[-1].astype(np.float32, copy=False)
    return np.zeros(extras_dim, dtype=np.float32)


def _apply_estimator_scaler(estimator: Any, arr: np.ndarray) -> np.ndarray:
    """Apply estimator scaler to a flattened 2D array (N, F)."""

    kind = getattr(estimator, "_scaler_kind_", None)
    if kind is None:
        return arr
    state = getattr(estimator, "_scaler_state_", {}) or {}
    if kind == "standard":
        mean = np.asarray(state.get("mean"), dtype=np.float32)
        var = np.asarray(state.get("M2"), dtype=np.float32)
        n = max(int(state.get("n", 1)), 1)
        if mean.size and var.size:
            std = np.sqrt(np.maximum(var / n, 1e-8)).astype(np.float32)
            return (arr - mean) / std
    elif kind == "minmax":
        mn = np.asarray(state.get("min"), dtype=np.float32)
        mx = np.asarray(state.get("max"), dtype=np.float32)
        if mn.size and mx.size:
            scale = np.where((mx - mn) > 1e-8, (mx - mn), 1.0)
            return (arr - mn) / scale
    elif kind == "custom" and hasattr(estimator.scaler, "transform"):
        return estimator.scaler.transform(arr)
    return arr


def rollout_supervised_extras(
    estimator: Any,
    X_obs: np.ndarray,
    *,
    config: SupervisedExtrasConfig,
    extras_cache: Optional[np.ndarray] = None,
    initial_extras: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Roll out supervised extras over a time-series.

    Parameters
    ----------
    estimator: fitted PSANN estimator
    X_obs: array-like of base observations with shape (N, base_dim)
    config: supervised extras configuration (primary/extras dims, etc.)
    extras_cache: optional cached extras state from a previous rollout
    initial_extras: optional explicit initial extras vector; overrides cache

    Returns
    -------
    primary_pred: np.ndarray, shape (N, primary_dim)
    extras_seq: np.ndarray, shape (N + 1, extras_dim) with extras_seq[0] being the
        initial extras and extras_seq[t+1] the predicted extras at step t
    extras_cache: np.ndarray, cached extras sequence (equal to extras_seq)
    """

    X_arr = np.asarray(X_obs, dtype=np.float32)
    cfg = ensure_supervised_extras_config(config)
    K = int(cfg.extras_dim)
    if K <= 0:
        raise ValueError("Estimator was not configured with extras; nothing to roll out.")

    if cfg.append_to_inputs:
        expected_base = cfg.base_dim
        if X_arr.ndim != 2 or X_arr.shape[1] != expected_base:
            raise ValueError(
                f"Expected base features with shape (N, {expected_base}) but received {X_arr.shape}"
            )
    else:
        if X_arr.ndim != 2 or X_arr.shape[1] != cfg.feature_dim:
            raise ValueError(
                f"Expected features with shape (N, {cfg.feature_dim}) but received {X_arr.shape}"
            )

    init_extras = _normalise_initial_extras(K, initial_extras=initial_extras, cache=extras_cache)
    N = int(X_arr.shape[0])

    primary = np.zeros((N, cfg.primary_dim), dtype=np.float32)
    extras_seq = np.zeros((N + 1, K), dtype=np.float32)
    extras_seq[0] = init_extras

    model = estimator.model_
    if model is None:
        raise RuntimeError("Estimator has no trained model; call fit() first.")
    model.eval()
    device = estimator._device()

    extras_state = init_extras.astype(np.float32, copy=True)
    for t in range(N):
        if cfg.append_to_inputs:
            x_t = np.concatenate([X_arr[t], extras_state], axis=-1)
        else:
            x_t = X_arr[t]
        x_batch = x_t.reshape(1, -1)
        x_batch = _apply_estimator_scaler(estimator, x_batch)
        with torch.no_grad():
            torch_in = torch.from_numpy(x_batch).to(device)
            out = model(torch_in).cpu().numpy()[0]
        primary[t] = out[: cfg.primary_dim]
        extras_state = out[cfg.primary_dim : cfg.primary_dim + K]
        extras_seq[t + 1] = extras_state

    cache_arr = extras_seq.copy()
    return primary, extras_seq, cache_arr


__all__ = [
    "SupervisedExtrasConfig",
    "ensure_supervised_extras_config",
    "rollout_supervised_extras",
]
