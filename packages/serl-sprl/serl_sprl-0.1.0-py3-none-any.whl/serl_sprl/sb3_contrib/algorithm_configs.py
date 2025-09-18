from pydantic import BaseModel
from stable_baselines3.td3 import TD3
from stable_baselines3.a2c import A2C
from stable_baselines3.common.noise import NormalActionNoise

class TD3Config(BaseModel):
    total_timesteps: int
    learning_rate: float
    action_noise: NormalActionNoise
    policy_kwargs: dict
    batch_size: int
    gamma: float
    algorithm: TD3 = TD3
    policy: str = "MlpPolicy"
    buffer_size: int = 100000
    train_freq: int = 1
    gradient_steps: int = 1

class A2CConfig(BaseModel):
    total_timesteps: int
    learning_rate: float
    n_steps: int
    policy_kwargs: dict
    log_std_init: float
    gamma: float
    vf_coef: float
    max_grad_norm: float
    gae_lambda: float
    algorithm: A2C = A2C
    policy: str = "MlpPolicy"
    ent_coef: float = 0.0
    use_rms_prop: bool = True
    normalize_advantage: bool = False
    squash_output: bool = True