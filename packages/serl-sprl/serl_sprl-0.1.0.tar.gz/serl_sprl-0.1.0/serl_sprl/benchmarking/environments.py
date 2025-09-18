from typing import Literal
import gymnasium as gym 
from stable_baselines3.common.vec_env import DummyVecEnv
from typing import Callable
from serl_sprl.projection.projection_wrappers import *
from serl_sprl.sets import Zonotope

def transform_action_space_fn(action: np.ndarray, action_limits: list):
    """Convert action from [-1, 1] to [u_min, u_max]."""
    # [-1,1] -> [u_min, u_max]
    return np.clip(
        ((action + 1) / 2) * (action_limits[1] - action_limits[0]) + action_limits[0], action_limits[0], action_limits[1]
    )

def inv_transform_action_space_fn(action: np.ndarray, action_limits: list):
    """Convert action from [u_min, u_max] to [-1, 1]."""
    # [a_min, a_max] -> [-1,1]
    return np.clip(((action - action_limits[0]) / (action_limits[1] - action_limits[0])) * 2 - 1, -1, 1)

class BaseCreator:
    def __init__(self, env_id: str):
        self.env_id = env_id

    def create_env(self, env_config: dict, wrapper_kwargs: dict = None, num_envs: int = 1) -> gym.Env:
        def make_env(rank: int) -> Callable[[], gym.Env]:
            def _init() -> gym.Env:
                # ToDo: check that environment is registered
                env = gym.make(self.env_id, **env_config)
                env = gym.wrappers.TimeLimit(env, env_config.max_rollout_steps)
                # transformation into zonotopes
                u_eq = (env.unwrapped.action_space.high + env.unwrapped.action_space.low) / 2
                allowable_input_set_factors = np.array((env.unwrapped.action_space.high - env.unwrapped.action_space.low) / 2).T
                u_space_zono = Zonotope(G=np.eye(u_eq.shape[0]) * allowable_input_set_factors, c=u_eq.reshape((-1, 1)))
                noise_set_zonotope = Zonotope(G = env_config.get("w", np.zeros(env.action_space.shape)) * np.eye(u_eq.shape[0]).T, c = np.zeros(u_eq.shape).reshape((-1, 1)))
                if wrapper_kwargs is not None:
                    wrapper_kwargs["noise_set_zonotope"] = noise_set_zonotope
                    wrapper_kwargs["u_space_zono"] = u_space_zono
                else:
                    wrapper_kwargs = {"noise_set_zonotope": noise_set_zonotope, "u_space_zono": u_space_zono}
                # wrap environment if needed
                env = self._wrap_env(env, wrapper_kwargs)
                # add monitor wrapper for logging
                env = gym.wrappers.Monitor(env, None)
                return env
            return _init
        return DummyVecEnv([make_env(i) for i in range(num_envs)])
    
    def _wrap_env(self, env: gym.Env) -> gym.Env:
        raise NotImplementedError

class BaselineCreator(BaseCreator):
    def _wrap_env(self, env: gym.Env, wrapper_kwargs: dict = None) -> gym.Env:
        # Create baseline environment without safeguarding
        alter_action_space = gym.spaces.Box(low=-1, high=1, shape=env.action_space.shape, dtype=wrapper_kwargs.get("dtype", env.action_space.dtype)) if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None
        env = InformerWrapper(
            env=env,
            alter_action_space=alter_action_space,
            transform_action_space_fn=transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
            inv_transform_action_space_fn=inv_transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
        )
    
class SERLEnvCreator(BaseCreator):
    def _wrap_env(self, env: gym.Env, wrapper_kwargs: dict = None) -> gym.Env:
        # Create SERL environment without any improvement strategy
        alter_action_space = gym.spaces.Box(low=-1, high=1, shape=env.action_space.shape, dtype=wrapper_kwargs.get("dtype", env.action_space.dtype)) if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None
        env = ActionProjectionWrapper(
            env,
            admissible_input_set=wrapper_kwargs.get("u_space_zono"),
            noise_set=wrapper_kwargs.get("noise_set_zonotope").map(getattr(env, "E_d")),
            safe_control_fn=wrapper_kwargs.get("safe_control_fn", None),
            alter_action_space=alter_action_space,
            transform_action_space_fn=transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
            inv_transform_action_space_fn=inv_transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
        )
        return env
    
class SERLPenaltyEnvCreator(BaseCreator):
    def _wrap_env(self, env: gym.Env, wrapper_kwargs: dict = None) -> gym.Env:
        # Create SERL environment with penalty improvement strategy
        alter_action_space = gym.spaces.Box(low=-1, high=1, shape=env.action_space.shape, dtype=wrapper_kwargs.get("dtype", env.action_space.dtype)) if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None
        env = ActionProjectionWrapper(
            env,
            admissible_input_set=wrapper_kwargs.get("u_space_zono"),
            noise_set=wrapper_kwargs.get("noise_set_zonotope").map(getattr(env, "E_d")),
            safe_control_fn=wrapper_kwargs.get("safe_control_fn", None),
            alter_action_space=alter_action_space,
            penalty_factor=wrapper_kwargs.get("penalty_factor", 0.0),  # Only difference to SERLEnvCreator
            transform_action_space_fn=transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
            inv_transform_action_space_fn=inv_transform_action_space_fn if wrapper_kwargs and wrapper_kwargs.get("scale_actions") else None,
        )
        return env
    
class EnvCreatorFactory:
    def __init__(self, approach: Literal["baseline", "serl", "sprl"], improvement_strategy: Literal["penalty", "psl", "penalty_critic", "none"], env_id: str):
        self.approach = approach
        self.improvement_strategy = improvement_strategy
        self.env_id = env_id

    def get_env_creator(self) -> BaseCreator:
        if self.approach == "baseline": 
            return BaselineCreator(self.env_id)
        elif self.approach == "serl":
            if self.improvement_strategy == "none":
                return SERLEnvCreator(self.env_id)
            elif self.improvement_strategy == "penalty":
                return SERLPenaltyEnvCreator(self.env_id)
            else: 
                raise ValueError(f"Unknown improvement strategy {self.improvement_strategy} for approach {self.approach}")
        elif self.approach == "sprl":
            if self.improvement_strategy == "none":
                return SPRLEnvCreator(self.env_id)
            elif self.improvement_strategy == "psl":
                return SPRLPslEnvCreator(self.env_id)
            elif self.improvement_strategy == "penalty_critic":
                return SPRLPenaltyCriticEnvCreator(self.env_id)
            else:
                raise ValueError(f"Unknown improvement strategy {self.improvement_strategy} for approach {self.approach}")