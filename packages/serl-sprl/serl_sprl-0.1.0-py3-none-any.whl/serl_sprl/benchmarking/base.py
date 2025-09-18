from serl_sprl.envs.configs import BaseEnvConfig
from serl_sprl.benchmarking.environments import EnvCreatorFactory

class Experiment:
    def __init__(self, env_factory: EnvCreatorFactory, env_config: BaseEnvConfig, algorithm_config: dict):
        self.env_creator = env_factory.get_env_creator()
        self.env = self.env_creator.create_env(env_config=env_config)
        self.algorithm_config = algorithm_config
    
    def run_training(self):
        # WandB stuff here
        # Set up model
        model = self.algorithm_config.get("algorithm")(
            seed=42,  # ToDo
            env=self.env,
            policy=self.algorithm_config.get("policy"),
            policy_kwargs=self.algorithm_config.get("policy_kwargs", {}),
            device="cpu",  # ToDo
            **self.algorithm_config.get("hyperparameters", {})
        )
        # Train model
        model.learn(total_timesteps=self.algorithm_config.get("total_timesteps", 100000))
