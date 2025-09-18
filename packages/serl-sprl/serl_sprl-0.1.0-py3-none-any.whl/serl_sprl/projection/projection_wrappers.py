import warnings

import cvxpy as cp
import gymnasium as gym
import numpy as np

from serl_sprl.projection.projection_helpers import create_problem

def fetch_fn(env, fn):
    if fn is not None:
        if isinstance(fn, str):
            fn = getattr(env, fn)
        if not callable(fn):
            raise ValueError(f"Attribute {fn} is not callable")
    return fn

class InformerWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        alter_action_space=None,
        transform_action_space_fn=None,
        inv_transform_action_space_fn=None,
    ):
        super().__init__(env)

        self._transform_action_space_fn = fetch_fn(self.env, transform_action_space_fn)
        self._inv_transform_action_space_fn = fetch_fn(self.env, inv_transform_action_space_fn)

        if not hasattr(self.env, "action_space"):
            warnings.warn("Environment has no attribute ``action_space``")

        if alter_action_space is not None:
            self.action_space = alter_action_space
            if transform_action_space_fn is None:
                warnings.warn("Set ``alter_action_space`` but no ``transform_action_space_fn``")

    def step(self, action):
        # Optional action transformation
        if self._transform_action_space_fn is not None:
            action = self._transform_action_space_fn(action, [self.unwrapped.action_space.low, self.unwrapped.action_space.high])

        obs, reward, done, truncated, info = self.env.step(action)
        info["baseline"] = {"policy_action": action, "env_reward": reward}
        self.unwrapped.last_action = self._inv_transform_action_space_fn(action, [self.unwrapped.action_space.low, self.unwrapped.action_space.high])

        return obs, reward, done, truncated, info


class ActionProjectionWrapper(gym.Wrapper):
    def __init__(
        self,
        env: gym.Env,
        admissible_input_set,
        penalty_factor: float = 0.0,
        noise_set=None,
        safe_control_fn=None,
        alter_action_space=None,
        transform_action_space_fn=None,
        inv_transform_action_space_fn=None,
    ):
        super().__init__(env)
        self._penalty_factor = penalty_factor
        self._safe_control_fn = fetch_fn(self.env, safe_control_fn)
        self._noise_set = noise_set
        self._input_set = admissible_input_set

        if alter_action_space is not None:
            self.action_space = alter_action_space
            if transform_action_space_fn is None or inv_transform_action_space_fn is None:
                warnings.warn(
                    "Set ``alter_action_space`` but no ``transform_action_space_fn``"
                    " or  ``inv_transform_action_space_fn``"
                )
            else:
                self._transform_action_space_fn = fetch_fn(self.env, transform_action_space_fn)
                self._inv_transform_action_space_fn = fetch_fn(self.env, inv_transform_action_space_fn)

        self._infeasible_step = False
        self.last_projected = False

        # As the solver is parametrized, we create the problem structures and get the path of the changeable variables
        # so we can update them in the future and them resolve the problem faster
        self.prob, self.u_rl_p, self.x_k_p, self.u = create_problem(
            c_u=self._input_set.c.flatten(),
            G_u=self._input_set.G,
            c_w=self._noise_set.c.flatten(),
            G_w_hat=self._noise_set.G,
            G_omega=self._safe_region.RCI_zonotope.G,
            c_omega=self._safe_region.RCI_zonotope.c.flatten(),
            A_hat=getattr(self.env, 'A_d'),
            B_hat=getattr(self.env, 'B_d'),
            u_eq=getattr(self.env, 'u_eq'),
            x_eq=getattr(self.env, 'x_eq'),
        )

    def punishment_fn(self, unsafe_action, safe_action):
        return -np.linalg.norm(unsafe_action - safe_action, 2) ** 2 * self._penalty_factor  # ToDo: This is a mistake, should not be squared. If we rerun experiments, change.

    def step(self, action):
        """Steps through the environment with the projection of the action`.
        Args:
            action: action to step through the environment (before being projected)
        Returns:
            (observation, reward, done, info)
        """
        assert not np.any(np.isnan(action)), "NaN in action"
        self._infeasible_step = False
        # Optional action transformation
        if self._transform_action_space_fn is not None:
            action = self._transform_action_space_fn(action, [self.unwrapped.action_space.low, self.unwrapped.action_space.high])
        # Check if action is safe
        potential_next_state = self.dynamics_fn(self.env, action)
        if not self._safe_region.contains(potential_next_state):
            # Change the values of the parametrized variables inside the solver
            self.u_rl_p.value = action
            state = getattr(self.unwrapped, "state")
            self.x_k_p.value = state

            # Run the solver with the new values
            try:
                self.prob.solve(verbose=False, solver=cp.GUROBI, TimeLimit=1.0)
                safe_action = self.u.value
            except cp.SolverError as e:
                print("Solver Error: {}".format(e))
                safe_action = self._safe_control_fn(self.env, self._safe_region)
                self._infeasible_step = True

            if np.any(np.isnan(safe_action)):
                safe_action = self._safe_control_fn(self.env, self._safe_region)
                self._infeasible_step = True

            obs, reward, done, truncated, info = self.env.step(safe_action)
            info["projection"] = {"env_reward": reward, "infeasible": self._infeasible_step}
            info["projection"]["safe_action"] = safe_action

            # Optional reward punishment
            punishment = self._punishment_fn(action, safe_action)
            info["projection"]["pun_reward"] = punishment
            reward += punishment
            self.last_projected = True
            info["projection"]["action_projected"] = True
            self.unwrapped.last_action = self._inv_transform_action_space_fn(safe_action)
        else:
            # action is safe
            obs, reward, done, truncated, info = self.env.step(action)
            info["projection"] = {"env_reward": reward, "pun_reward": 0.0, "infeasible": self._infeasible_step}
            info["projection"]["action_projected"] = False
            self.last_projected = False
            self.unwrapped.last_action = self._inv_transform_action_space_fn(action)

        info["projection"]["policy_action"] = action
        info["projection"]["last_projected"] = self.last_projected

        return obs, reward, done, truncated, info

    def project_action(self, current_state, unsafe_action) -> np.ndarray:
        punishment = 0.0
        if self._transform_action_space_fn is not None:
            unsafe_action = self._transform_action_space_fn(unsafe_action, [self.unwrapped.action_space.low, self.unwrapped.action_space.high])
        self.u_rl_p.value = unsafe_action
        self.x_k_p.value = current_state
        # Run the solver with the new values
        self.prob.solve(verbose=False, solver=cp.GUROBI, TimeLimit=1.0)
        safe_action = self.u.value
        # Optional reward punishment
        punishment = self._punishment_fn(unsafe_action, safe_action)
        if self._inv_transform_action_space_fn is not None:
            safe_action = self._inv_transform_action_space_fn(safe_action)
        return safe_action, punishment

    def get_projection_config(self) -> dict:
        config = dict()
        config["G_u"] = self._input_set.G
        config["c_u"] = self._input_set.c.flatten()
        config["c_w"] = self._noise_set.c.flatten()
        config["G_w_hat"] = self._noise_set.G
        config["G_omega"] = self._safe_region.RCI_zonotope.G
        config["c_omega"] = self._safe_region.RCI_zonotope.c.flatten()
        config["A_hat"] = getattr(self.env, 'A_d')
        config["B_hat"] = getattr(self.env, 'B_d')
        config["u_eq"] = getattr(self.env, 'u_eq')
        config["x_eq"] = getattr(self.env, 'x_eq')
        config["u_low"] = getattr(getattr(self.env, "action_space"), "low")
        config["u_high"] = getattr(getattr(self.env, "action_space"), "high")
        return config