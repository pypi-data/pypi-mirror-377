from os import path

import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Dict, Optional, Tuple, Union, Any, Callable
from stable_baselines3.common.vec_env import DummyVecEnv

from serl_sprl.envs.configs import BaseEnvConfig, BaseProjectionConfig
from serl_sprl.envs.safe_region import ControlInvariantSetZonotope

def safe_control_fn(env, safe_region):
    # Sample a safe action from the failsafe controller
    state = env.get_attr("state")[0] if isinstance(env, DummyVecEnv) else env.state
    return safe_region.sample_ctrl(state)

class PendulumEnvConfig(BaseEnvConfig):
    id: str = 'envs/PendulumEnv'
    safe_region = ControlInvariantSetZonotope(
            S_ctrl_csv='matlab/S_ctrl_Pendulum.csv',
            S_RCI_csv='matlab/S_RCI_Pendulum.csv',
            x_goal=[0, 0],
            x_lim_low=[-2.0, -6.5],
            x_lim_high=[2.0 , 6.5],
        )
    randomize: bool
    collision_reward: float = 0.0
    w: list[float] = [0.1, 0.1]
    # Dynamics
    dt: float = 0.05

class PendulumProjConfig(BaseProjectionConfig):
    safe_control_fn: Callable = safe_control_fn


class SimplePendulumEnv(gym.Env):
    """An inverted pendulum environment.

    Characteristica:
        - random initial state (optional)
    """
    _dtype = np.float32

    def __init__(
            self,
            dt: float = 0.05,
            randomize_env: bool = True,
            start_state: np.ndarray = np.array([0, 0], dtype=_dtype),
            collision_reward: float = 0.0,
            state_constraints: Optional[np.ndarray] = None,
            safe_region: Optional[ControlInvariantSetZonotope] = None,
            seed: int = 42
    ):

        self._safe_region = safe_region
        self.rnd_seed = seed

        self.l = 1.
        self.m = 1.
        self.g = 9.81
        self.dt = dt
        self.randomize_env = randomize_env
        self.start_state = np.array(start_state, dtype=self._dtype)
        self.collision_reward = collision_reward

        # discretized dynamics
        self.A_d = np.array([[1.01845021, 0.05030713], [0.74026937, 1.01845021]])
        self.B_d = np.array([[0.00376151], [0.15092138]])
        self.x_eq = np.array([0, 0])
        self.u_eq = np.array([0])
        # "action noise" will only influence the velocity
        self.E_d = np.array([[1], [1]])

        # In the original gymnasium env this is 2.0
        max_torque = 8
        self.action_space = spaces.Box(
            low=-max_torque,
            high=max_torque,
            shape=(1,),
            dtype=self._dtype,
            seed=self.rnd_seed
        )

        # ToDo: fix max_speed?
        obs_high = np.array([10.0 * np.pi, np.inf], dtype=self._dtype)
        self.state_constraints = state_constraints
        self.observation_space = spaces.Box(low=-obs_high, high=obs_high, dtype=self._dtype, seed=self.rnd_seed)

        self.state = None
        self.viewer = None
        self._collision = False
        
        # for saving last actions:
        self._last_action = None
        self._input_change = None

    def reset(
            self,
            seed: Union[int, None] = None,
            options: Union[Dict[str, Any], None] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)
        self._last_action = None
        self._is_safety_violated = None

        if self.randomize_env:
            self.state = np.asarray(self._safe_region.sample())
        else:
            self.state = self.start_state
        obs_info = self._get_info()
        self._collision = False
        return self._get_obs(), obs_info

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        self._collision = False
        # ToDo: This does not implement noise??
        theta, thdot = self.state
        # ToDo: clip action?
        self._input_change = (action - self._last_action)/self.dt if self._last_action is not None else None
        self._last_action = action
        self.state = self.dynamics_fn(theta, thdot, action)
        if self.collision_check_fn():
            self._collision = True
        # Note: This differs from gymnasium - we compute the reward for the next state, not the current one.
        reward = self._get_reward(*self.state, torque=action)
        done = False
        truncated = False
        return self._get_obs(), reward, done, truncated, self._get_info()

    def collision_check_fn(self):
        if self._safe_region is not None:
            collision = not self._safe_region.contains(self.state)
        else:
            collision = np.any(
                self.state <= self.state_constraints[0]) or np.any(self.state >= self.state_constraints[1])
        return collision

    def _get_info(self) -> dict:
        return {
            "collision": self._collision,
            "input_change": self._input_change,
        }

    def _get_obs(self):
        theta, thdot = self.state
        # return np.array([np.cos(theta), np.sin(theta), thdot], dtype=np.float32)
        return self.state.copy()

    def dynamics_fn(self, theta, thdot, torque):

        # sb3.common.distributions
        if isinstance(torque, np.ndarray):
            torque = torque.item()

        new_thdot = thdot + self.dt * (3 * self.g / (2 * self.l) * np.sin(theta) + 3. / (self.m * self.l ** 2) * torque)
        # ToDo: clip to max_speed?
        new_theta = theta + self.dt * new_thdot
        new_theta = self.angle_normalize(new_theta)
        return np.array([new_theta, new_thdot])

    @staticmethod
    def angle_normalize(x):
        return ((x + np.pi) % (2 * np.pi)) - np.pi

    def _get_reward(self, theta, thdot, torque):
        rew = -(self.angle_normalize(theta) ** 2 + 0.1 * thdot ** 2 + 0.001 * (torque ** 2))
        if self._collision:
            rew += self.collision_reward
        return float(rew)

    def render(self, mode="human", **kwargs):

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(500, 500)
            self.viewer.set_bounds(-2.2, 2.2, -2.2, 2.2)

            rod = rendering.make_capsule(1, .035)
            rod.set_color(0, 0, 0)
            self.pole_transform = rendering.Transform()
            rod.add_attr(self.pole_transform)
            self.viewer.add_geom(rod)

            self.mass = rendering.make_circle(.15)
            self.mass.set_color(0/255, 92/255, 171/255)
            self.mass_transform = rendering.Transform()
            self.mass.add_attr(self.mass_transform)
            self.viewer.add_geom(self.mass)

            axle = rendering.make_circle(.035)
            axle.set_color(0, 0, 0)
            self.viewer.add_geom(axle)

            self.img_black = rendering.Image(path.join(path.dirname(__file__), "assets/clockwise.png"), 1., 1.)
            self.imgtrans_black = rendering.Transform()
            self.img_black.add_attr(self.imgtrans_black)
            self.imgtrans_black.scale = (0., 0.)

        if self._last_action is not None:
            self.viewer.add_onetime(self.img_black)
            self.imgtrans_black.scale = (-self._last_action/8, -abs(self._last_action)/8)

        theta_trans = -self.state[0] + np.pi / 2
        self.pole_transform.set_rotation(theta_trans)
        self.mass_transform.set_translation(np.cos(theta_trans), np.sin(theta_trans))

        if not self._is_safety_violated and self.state not in self._safe_region:
            self.mass.set_color(227/255, 27/255, 35/255)
            self._is_safety_violated = True

        return self.viewer.render(return_rgb_array=mode == "rgb_array")

    def close(self):
        if self.viewer is not None:
            self.viewer.close()
            self.viewer = None