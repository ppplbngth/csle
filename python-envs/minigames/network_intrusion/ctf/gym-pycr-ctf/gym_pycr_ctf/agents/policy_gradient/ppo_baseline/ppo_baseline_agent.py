"""
An agent for the pycr-ctf env that uses the PPO Policy Gradient algorithm from OpenAI stable baselines
"""
import time
import torch
import math

from gym_pycr_ctf.rendering.video.pycr_ctf_monitor import PyCrCTFMonitor
from gym_pycr_ctf.dao.experiment.experiment_result import ExperimentResult
from gym_pycr_ctf.agents.train_agent import TrainAgent
from gym_pycr_ctf.agents.config.agent_config import AgentConfig
from gym_pycr_ctf.agents.policy_gradient.ppo_baseline.impl.ppo.ppo import PPO
from gym_pycr_ctf.agents.openai_baselines.common.vec_env.dummy_vec_env import DummyVecEnv
from gym_pycr_ctf.agents.openai_baselines.common.vec_env.subproc_vec_env import SubprocVecEnv
from gym_pycr_ctf.dao.agent.train_mode import TrainMode

class PPOBaselineAgent(TrainAgent):
    """
    An agent for the pycr-ctf env that uses the PPO Policy Gradient algorithm from OpenAI stable baselines
    """

    def __init__(self, env, attacker_agent_config: AgentConfig,
                 defender_agent_config: AgentConfig,
                 eval_env, train_mode: TrainMode = TrainMode.TRAIN_ATTACKER):
        """
        Initialize environment and hyperparameters

        :param attacker_agent_config: the configuration
        """
        super(PPOBaselineAgent, self).__init__(env, attacker_agent_config,
                                               defender_agent_config,
                                               eval_env, train_mode)

    def train(self) -> ExperimentResult:
        """
        Starts the training loop and returns the result when complete

        :return: the training result
        """

        # Setup Attacker


        # Custom MLP policy for attacker
        attacker_net_arch = []
        attacker_pi_arch = []
        attacker_vf_arch = []
        for l in range(self.attacker_config.shared_layers):
            attacker_net_arch.append(self.attacker_config.shared_hidden_dim)
        for l in range(self.attacker_config.pi_hidden_layers):
            attacker_pi_arch.append(self.attacker_config.pi_hidden_dim)
        for l in range(self.attacker_config.vf_hidden_layers):
            attacker_vf_arch.append(self.attacker_config.vf_hidden_dim)

        net_dict_attacker = {"pi": attacker_pi_arch, "vf": attacker_vf_arch}
        attacker_net_arch.append(net_dict_attacker)

        policy_kwargs_attacker = dict(activation_fn=self.get_hidden_activation_attacker(), net_arch=attacker_net_arch)
        device_attacker = "cpu" if not self.attacker_config.gpu else "cuda:" + str(self.attacker_config.gpu_id)
        policy_attacker = "MlpPolicy"

        if self.attacker_config.lr_progress_decay:
            temp = self.attacker_config.alpha
            lr_decay_func = lambda x: temp * math.pow(x, self.attacker_config.lr_progress_power_decay)
            self.attacker_config.alpha = lr_decay_func

        # Setup Defender

        # Custom MLP policy for attacker
        defender_net_arch = []
        defender_pi_arch = []
        defender_vf_arch = []
        for l in range(self.defender_config.shared_layers):
            defender_net_arch.append(self.defender_config.shared_hidden_dim)
        for l in range(self.defender_config.pi_hidden_layers):
            defender_pi_arch.append(self.defender_config.pi_hidden_dim)
        for l in range(self.defender_config.vf_hidden_layers):
            defender_vf_arch.append(self.defender_config.vf_hidden_dim)

        net_dict_defender = {"pi": defender_pi_arch, "vf": defender_vf_arch}
        defender_net_arch.append(net_dict_defender)

        policy_kwargs_defender = dict(activation_fn=self.get_hidden_activation_defender(), net_arch=defender_net_arch)
        device_defender = "cpu" if not self.defender_config.gpu else "cuda:" + str(self.defender_config.gpu_id)
        policy_defender = "MlpPolicy"

        # Create model

        model = PPO(policy_attacker, policy_defender,
                    self.env,
                    batch_size=self.attacker_config.mini_batch_size,
                    attacker_learning_rate=self.attacker_config.alpha,
                    defender_learning_rate=self.defender_config.alpha,
                    n_steps=self.attacker_config.batch_size,
                    n_epochs=self.attacker_config.optimization_iterations,
                    attacker_gamma=self.attacker_config.gamma,
                    defender_gamma=self.defender_config.gamma,
                    attacker_gae_lambda=self.attacker_config.gae_lambda,
                    defender_gae_lambda=self.defender_config.gae_lambda,
                    attacker_clip_range=self.attacker_config.eps_clip,
                    defender_clip_range=self.defender_config.eps_clip,
                    attacker_max_grad_norm=self.attacker_config.max_gradient_norm,
                    defender_max_grad_norm=self.defender_config.max_gradient_norm,
                    verbose=1,
                    seed=self.attacker_config.random_seed,
                    attacker_policy_kwargs=policy_kwargs_attacker,
                    defender_policy_kwargs=policy_kwargs_defender,
                    device=device_attacker,
                    attacker_agent_config=self.attacker_config,
                    defender_agent_config=self.defender_config,
                    attacker_vf_coef=self.attacker_config.vf_coef,
                    defender_vf_coef=self.defender_config.vf_coef,
                    attacker_ent_coef=self.attacker_config.ent_coef,
                    defender_ent_coef=self.defender_config.ent_coef,
                    use_sde=self.attacker_config.use_sde,
                    sde_sample_freq=self.attacker_config.sde_sample_freq,
                    env_2=self.eval_env,
                    train_mode = self.train_mode
                    )

        if self.attacker_config.load_path is not None:
            PPO.load(self.attacker_config.load_path, policy_attacker, agent_config=self.attacker_config)

        elif self.defender_config.load_path is not None:
            PPO.load(self.defender_config.load_path, policy_defender, agent_config=self.defender_config)

        # Eval config
        time_str = str(time.time())

        if self.train_mode == TrainMode.TRAIN_ATTACKER or self.train_mode == TrainMode.SELF_PLAY:
            video_dir = self.attacker_config.video_dir
            video_frequency = self.attacker_config.video_frequency
            video_fps = self.attacker_config.video_fps
            total_timesteps = self.attacker_config.num_episodes
            train_log_frequency = self.attacker_config.train_log_frequency
            eval_frequency = self.attacker_config.eval_frequency
            eval_episodes = self.attacker_config.eval_episodes
            save_dir = self.attacker_config.save_dir
        else:
            video_dir = self.defender_config.video_dir
            video_frequency = self.defender_config.video_frequency
            video_fps = self.defender_config.video_fps
            total_timesteps = self.defender_config.num_episodes
            train_log_frequency = self.defender_config.train_log_frequency
            eval_frequency = self.defender_config.eval_frequency
            eval_episodes = self.defender_config.eval_episodes
            save_dir = self.defender_config.save_dir

        if video_dir is None:
            raise AssertionError("Video is set to True but no video_dir is provided, please specify "
                                 "the video_dir argument")
        if isinstance(self.env, DummyVecEnv):
            train_eval_env_i = self.env
            train_eval_env = train_eval_env_i
        elif isinstance(self.env, SubprocVecEnv):
            train_eval_env_i = self.env
            train_eval_env = train_eval_env_i
        else:
            train_eval_env_i = self.env
            if train_eval_env_i is not None:
                train_eval_env = PyCrCTFMonitor(train_eval_env_i, video_dir + "/" + time_str, force=True,
                                          video_frequency=video_frequency, openai_baseline=True)
                train_eval_env.metadata["video.frames_per_second"] = video_fps
            else:
                train_eval_env = None

        eval_env = None
        if isinstance(self.eval_env, DummyVecEnv) or isinstance(self.eval_env, SubprocVecEnv):
            eval_env = self.eval_env
        else:
            if self.eval_env is not None:
                eval_env = PyCrCTFMonitor(self.eval_env, video_dir + "/" + time_str, force=True,
                                                    video_frequency=video_frequency, openai_baseline=True)
                eval_env.metadata["video.frames_per_second"] = video_fps

        model.learn(total_timesteps=total_timesteps,
                    log_interval=train_log_frequency,
                    eval_freq=eval_frequency,
                    n_eval_episodes=eval_episodes,
                    eval_env=train_eval_env,
                    eval_env_2=eval_env
                    )

        if self.attacker_config is not None:
            self.attacker_config.logger.info("Training Complete")
        if self.defender_config is not None:
            self.defender_config.logger.info("Training Complete")

        # Save networks
        try:
            model.save_model()
        except Exception as e:
            print("There was en error saving the model:{}".format(str(e)))

        # Save other game data
        if save_dir is not None:
            time_str = str(time.time())
            model.train_result.to_csv(save_dir + "/" + time_str + "_train_results_checkpoint.csv")
            model.eval_result.to_csv(save_dir + "/" + time_str + "_eval_results_checkpoint.csv")

        self.train_result = model.train_result
        self.eval_result = model.eval_result
        return model.train_result

    def get_hidden_activation_attacker(self):
        """
        Interprets the hidden activation

        :return: the hidden activation function
        """
        return torch.nn.Tanh
        if self.attacker_config.hidden_activation == "ReLU":
            return torch.nn.ReLU
        elif self.attacker_config.hidden_activation == "LeakyReLU":
            return torch.nn.LeakyReLU
        elif self.attacker_config.hidden_activation == "LogSigmoid":
            return torch.nn.LogSigmoid
        elif self.attacker_config.hidden_activation == "PReLU":
            return torch.nn.PReLU
        elif self.attacker_config.hidden_activation == "Sigmoid":
            return torch.nn.Sigmoid
        elif self.attacker_config.hidden_activation == "Softplus":
            return torch.nn.Softplus
        elif self.attacker_config.hidden_activation == "Tanh":
            return torch.nn.Tanh
        else:
            raise ValueError("Activation type: {} not recognized".format(self.attacker_config.hidden_activation))

    def get_hidden_activation_defender(self):
        """
        Interprets the hidden activation

        :return: the hidden activation function
        """
        return torch.nn.Tanh
        if self.defender_config.hidden_activation == "ReLU":
            return torch.nn.ReLU
        elif self.defender_config.hidden_activation == "LeakyReLU":
            return torch.nn.LeakyReLU
        elif self.defender_config.hidden_activation == "LogSigmoid":
            return torch.nn.LogSigmoid
        elif self.defender_config.hidden_activation == "PReLU":
            return torch.nn.PReLU
        elif self.defender_config.hidden_activation == "Sigmoid":
            return torch.nn.Sigmoid
        elif self.defender_config.hidden_activation == "Softplus":
            return torch.nn.Softplus
        elif self.defender_config.hidden_activation == "Tanh":
            return torch.nn.Tanh
        else:
            raise ValueError("Activation type: {} not recognized".format(self.defender_config.hidden_activation))


    def get_action(self, s, eval=False, attacker=True) -> int:
        raise NotImplemented("not implemented")

    def eval(self, log=True) -> ExperimentResult:
        raise NotImplemented("not implemented")