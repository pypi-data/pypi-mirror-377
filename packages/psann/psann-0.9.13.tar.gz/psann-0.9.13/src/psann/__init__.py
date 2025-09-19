"""PSANN: Parameterized Sine-Activated Neural Networks.

Sklearn-style estimators powered by PyTorch.
"""

from .sklearn import PSANNRegressor, ResPSANNRegressor
from .lsm import LSM, LSMExpander, LSMConv2d, LSMConv2dExpander
from .activations import SineParam
from .types import ActivationConfig
from .episodes import EpisodeTrainer, EpisodeConfig, portfolio_log_return_reward, make_episode_trainer_from_estimator
from .augmented import PredictiveExtrasTrainer, PredictiveExtrasConfig, make_predictive_extras_trainer_from_estimator
from .extras import SupervisedExtrasConfig, ensure_supervised_extras_config, rollout_supervised_extras
from .tokenizer import SimpleWordTokenizer
from .embeddings import SineTokenEmbedder
from .lm import PSANNLanguageModel, LMConfig

__all__ = [
    "PSANNRegressor",
    "ResPSANNRegressor",
    "LSM",
    "LSMExpander",
    "LSMConv2d",
    "LSMConv2dExpander",
    "SineParam",
    "ActivationConfig",
    "EpisodeTrainer",
    "EpisodeConfig",
    "portfolio_log_return_reward",
    "make_episode_trainer_from_estimator",
    "PredictiveExtrasTrainer",
    "PredictiveExtrasConfig",
    "make_predictive_extras_trainer_from_estimator",
    "SupervisedExtrasConfig",
    "ensure_supervised_extras_config",
    "rollout_supervised_extras",
    "SimpleWordTokenizer",
    "SineTokenEmbedder",
    "PSANNLanguageModel",
    "LMConfig",
]

__version__ = "0.9.13"
