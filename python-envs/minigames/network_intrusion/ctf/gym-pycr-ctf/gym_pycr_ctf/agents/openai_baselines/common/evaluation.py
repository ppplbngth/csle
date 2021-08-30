import typing
from typing import Callable, List, Optional, Tuple, Union

import gym
import numpy as np
import time
from gym_pycr_ctf.agents.openai_baselines.common.vec_env import VecEnv
from gym_pycr_ctf.dao.network.env_config import EnvConfig

if typing.TYPE_CHECKING:
    from gym_pycr_ctf.agents.openai_baselines.common.base_class import BaseAlgorithm
import gym_pycr_ctf.constants.constants as constants
from gym_pycr_ctf.agents.config.agent_config import AgentConfig
from gym_pycr_ctf.agents.openai_baselines.common.vec_env.dummy_vec_env import DummyVecEnv
from gym_pycr_ctf.agents.openai_baselines.common.vec_env.subproc_vec_env import SubprocVecEnv
from gym_pycr_ctf.dao.agent.train_mode import TrainMode
from gym_pycr_ctf.dao.agent.train_agent_log_dto import TrainAgentLogDTO

def evaluate_policy(model: "BaseAlgorithm", env: Union[gym.Env, VecEnv], env_2: Union[gym.Env, VecEnv],
                    n_eval_episodes : int=10,
                    deterministic : bool= True,
                    render : bool =False, callback: Optional[Callable] = None,
                    reward_threshold: Optional[float] = None,
                    return_episode_rewards: bool = False, attacker_agent_config : AgentConfig = None,
                    train_episode = 1, env_config = None, env_configs = None):
    """
    Runs policy for ``n_eval_episodes`` episodes and returns average reward.
    This is made to work only with one env.

    :param model: (BaseRLModel) The RL agent you want to evaluate.
    :param env: (gym.Env or VecEnv) The gym environment. In the case of a ``VecEnv``
        this must contain only one environment.
    :param env_2: (gym.Env or VecEnv) The second gym environment. In the case of a ``VecEnv``
        this must contain only one environment.
    :param n_eval_episodes: (int) Number of episode to evaluate the agent
    :param deterministic: (bool) Whether to use deterministic or stochastic actions
    :param render: (bool) Whether to render the environment or not
    :param callback: (callable) callback function to do additional checks,
        called after each step.
    :param reward_threshold: (float) Minimum expected reward per episode,
        this will raise an error if the performance is not met
    :param return_episode_rewards: (bool) If True, a list of reward per episode
        will be returned instead of the mean.
    :return: (float, float) Mean reward per episode, std of reward per episode
        returns ([float], [int]) when ``return_episode_rewards`` is True
    """
    eval_mean_reward, eval_std_reward = -1, -1
    train_eval_mean_reward, train_eval_std_reward = _eval_helper(env=env, attacker_agent_config=attacker_agent_config,
                                                                 n_eval_episodes=n_eval_episodes,
                                                                 deterministic=deterministic,
                                                                 callback=callback, train_episode=train_episode,
                                                                 model=model, env_config=env_config,
                                                                 env_configs=env_configs)

    if env_2 is not None:
        randomize_starting_states = []
        for i in range(env_2.num_envs):
            randomize_starting_states.append(env_2.envs[i].env_config.randomize_attacker_starting_state)
            env_2.envs[i].env_config.randomize_attacker_starting_state = False

        eval_mean_reward, eval_std_reward = _eval_helper(
            env=env_2, attacker_agent_config=attacker_agent_config, n_eval_episodes=n_eval_episodes,  deterministic=deterministic,
            callback=callback, train_episode=train_episode, model=model, env_config=env_config,
            env_configs=env_configs)

        for i in range(env_2.num_envs):
            env_2.envs[i].env_config.randomize_attacker_starting_state = randomize_starting_states[i]
    return train_eval_mean_reward, train_eval_std_reward, eval_mean_reward, eval_std_reward


def _eval_helper(env, attacker_agent_config: AgentConfig, model, n_eval_episodes, deterministic,
                 callback, train_episode, env_config, env_configs,
                 train_mode: TrainMode = TrainMode.TRAIN_ATTACKER,
                 train_dto : TrainAgentLogDTO = None):
    attacker_agent_config.logger.info("Starting Evaluation")

    model.num_eval_episodes = 0
    if attacker_agent_config.eval_episodes < 1:
        return

    done = False
    state = None

    # Tracking metrics
    episode_rewards = []
    episode_steps = []
    episode_flags = []
    episode_flags_percentage = []
    eval_episode_rewards_env_specific = {}
    eval_episode_steps_env_specific = {}
    eval_episode_flags_env_specific = {}
    eval_episode_flags_percentage_env_specific = {}

    if env.num_envs == 1 and not isinstance(env, SubprocVecEnv):
        env.envs[0].enabled = True
        env.envs[0].stats_recorder.closed = False
        env.envs[0].episode_id = 0


    for episode in range(n_eval_episodes):
        infos = np.array([{constants.INFO_DICT.NON_LEGAL_ACTIONS: env.initial_illegal_actions} for i in range(env.num_envs)])

        for i in range(env.num_envs):
            if env_configs is not None:
                if i < len(env_configs):
                    env_conf = env_configs[i]
                else:
                    env_conf = env_configs[0]
            else:
                env_conf = env_config
            if isinstance(env, SubprocVecEnv):
                obs = env.eval_reset(idx=i)
            elif isinstance(env, DummyVecEnv):
                obs = env.envs[i].reset()
            done = False
            state = None
            env_state = None
            episode_reward = 0.0
            episode_length = 0
            time_str = str(time.time())
            while not done:
                if isinstance(env, DummyVecEnv):
                    env_state = env.envs[i].env_state

                if env.num_envs == 1 and not isinstance(env, SubprocVecEnv) and attacker_agent_config.eval_render:
                    time.sleep(1)
                    env.render()

                actions, state = model.predict(obs, state=state, deterministic=deterministic, infos=infos,
                                               env_config=env_conf,
                                               env_configs=env_configs, env=env, env_idx=i,
                                               env_state=env_state)
                action = actions[0]
                if isinstance(env, SubprocVecEnv):
                    obs, reward, done, _info = env.eval_step(action, idx=i)
                elif isinstance(env, DummyVecEnv):
                    obs, reward, done, _info = env.envs[i].step(action)
                infos = [_info]
                episode_reward += reward
                episode_length += 1

            # Render final frame when game completed
            if env.num_envs == 1 and attacker_agent_config.eval_render:
                env.render()

            # Record episode metrics
            episode_rewards.append(episode_reward)
            episode_steps.append(episode_length)
            episode_flags.append(_info[constants.INFO_DICT.FLAGS])
            episode_flags_percentage.append(_info[constants.INFO_DICT.FLAGS] / env_conf.num_flags)
            eval_episode_rewards_env_specific, eval_episode_steps_env_specific, \
            eval_episode_flags_env_specific, eval_episode_flags_percentage_env_specific = \
                train_dto.eval_update_env_specific_metrics(env_conf, eval_episode_rewards_env_specific,
                                                 eval_episode_steps_env_specific, eval_episode_flags_env_specific,
                                                 eval_episode_flags_percentage_env_specific, episode_reward, episode_length,
                                                 _info, i)

            if isinstance(env, SubprocVecEnv):
                obs = env.eval_reset(idx=i)
            elif isinstance(env, DummyVecEnv):
                obs = env.envs[i].reset()
            if env.num_envs == 1:
                env.close()

            # Update eval stats
            model.num_eval_episodes += 1
            model.num_eval_episodes_total += 1


            # Save gifs
            if env.num_envs == 1 and not isinstance(env, SubprocVecEnv) and attacker_agent_config.gifs or attacker_agent_config.video:
                # Add frames to tensorboard
                for idx, frame in enumerate(env.envs[0].episode_frames):
                    model.tensorboard_writer.add_image(str(train_episode) + "_eval_frames/" + str(idx),
                                                       frame, global_step=train_episode,
                                                       dataformats="HWC")

                # Save Gif
                env.envs[0].generate_gif(attacker_agent_config.gif_dir + "episode_" + str(train_episode) + "_"
                                         + time_str + ".gif", attacker_agent_config.video_fps)
        # Log average metrics every <self.config.eval_log_frequency> episodes
        if episode % attacker_agent_config.eval_log_frequency == 0:
            model.log_metrics_attacker(iteration=episode, result=model.eval_result, episode_rewards=episode_rewards,
                                       episode_steps=episode_steps, eval=True, episode_flags=episode_flags,
                                       episode_flags_percentage=episode_flags_percentage)

    # Log average eval statistics
    model.log_metrics_attacker(iteration=train_episode, result=model.eval_result, episode_rewards=episode_rewards,
                               episode_steps=episode_steps, eval=True, episode_flags=episode_flags,
                               episode_flags_percentage=episode_flags_percentage)

    mean_reward = np.mean(episode_rewards)
    std_reward = np.std(episode_rewards)

    attacker_agent_config.logger.info("Evaluation Complete")
    print("Evaluation Complete")
    # env.close()
    # env.reset()
    return mean_reward, std_reward


def quick_evaluate_policy(attacker_model: "BaseAlgorithm", defender_model: "BaseAlgorithm",
                          env: Union[gym.Env, VecEnv], env_2: Union[gym.Env, VecEnv],
                          n_eval_episodes_train : int=10, n_eval_episodes_eval2 : int=10,
                          deterministic : bool= True, attacker_agent_config : AgentConfig = None,
                          defender_agent_config : AgentConfig = None,
                          env_config: EnvConfig = None, env_configs : List[EnvConfig] = None,
                          eval_env_config: EnvConfig = None, eval_envs_configs: List[EnvConfig] = None,
                          train_mode: TrainMode = TrainMode.TRAIN_ATTACKER,
                          train_dto : TrainAgentLogDTO = None
                          ):
    """
    Runs policy for ``n_eval_episodes`` episodes and returns average reward.
    This is made to work only with one env.

    :param attacker_model: (BaseRLModel) The RL agent you want to evaluate.
    :param env: (gym.Env or VecEnv) The gym environment. In the case of a ``VecEnv``
        this must contain only one environment.
    :param n_eval_episodes_train: (int) Number of episode to evaluate the agent
    :param deterministic: (bool) Whether to use deterministic or stochastic actions
    :param attacker_agent_config: agent config
    :return: episode_rewards, episode_steps, episode_flags_percentage, episode_flags
    """
    randomize_starting_states = []
    simulate_snort = []
    for i in range(env.num_envs):
        if isinstance(env, DummyVecEnv):
            randomize_starting_states.append(env.envs[i].env_config.randomize_attacker_starting_state)
            simulate_snort.append(env.envs[i].env_config.snort_baseline_simulate)
            env.envs[i].env_config.randomize_attacker_starting_state = False
            env.envs[i].env_config.snort_baseline_simulate = False
        elif isinstance(env, SubprocVecEnv):
            randomize_starting_states = env.get_randomize_starting_state()
            simulate_snort = env.get_snort_baseline_simulate()
            env.set_randomize_starting_state(False)
            env.set_snort_baseline_simulate(False)


    train_dto = _quick_eval_helper(
        env=env, attacker_model=attacker_model, defender_model=defender_model,
        n_eval_episodes=n_eval_episodes_train, deterministic=deterministic, env_config=env_config, train_mode=train_mode,
        env_configs =env_configs,
        train_log_dto=train_dto, eval_2=False)

    for i in range(env.num_envs):
        if isinstance(env, DummyVecEnv):
            env.envs[i].env_config.randomize_attacker_starting_state = randomize_starting_states[i]
            env.envs[i].env_config.snort_baseline_simulate = simulate_snort[i]
        elif isinstance(env, SubprocVecEnv):
            env.set_randomize_starting_state(randomize_starting_states[0])
            env.set_snort_baseline_simulate(simulate_snort[0])

    if env_2 is not None:
        randomize_starting_states = []
        simulate_snort = []
        for i in range(env_2.num_envs):
            if isinstance(env, DummyVecEnv):
                randomize_starting_states.append(env_2.envs[i].env_config.randomize_attacker_starting_state)
                simulate_snort.append(env_2.envs[i].env_config.snort_baseline_simulate)
                env_2.envs[i].env_config.randomize_attacker_starting_state = False
                env_2.envs[i].env_config.snort_baseline_simulate = False
            elif isinstance(env, SubprocVecEnv):
                randomize_starting_states = env_2.get_randomize_starting_state()
                simulate_snort = env_2.get_snort_baseline_simulate()
                env_2.set_randomize_starting_state(False)
                env_2.set_snort_baseline_simulate(False)

        train_dto = _quick_eval_helper(
            env=env_2, attacker_model=attacker_model, defender_model=defender_model,
            n_eval_episodes=n_eval_episodes_eval2, deterministic=deterministic, env_config=eval_env_config,
            train_mode=train_mode,
            env_configs=eval_envs_configs,
            emulation_env=True, eval_2=True, train_log_dto=train_dto
        )
        for i in range(env_2.num_envs):
            if isinstance(env, DummyVecEnv):
                env_2.envs[i].env_config.randomize_attacker_starting_state = randomize_starting_states[i]
                env_2.envs[i].env_config.snort_baseline_simulate = simulate_snort[i]
            elif isinstance(env, SubprocVecEnv):
                env_2.set_randomize_starting_state(randomize_starting_states[0])
                env_2.set_snort_baseline_simulate(simulate_snort[0])

    return train_dto


def _quick_eval_helper(env, attacker_model, defender_model,
                       n_eval_episodes, deterministic, env_config, train_mode, env_configs = None,
                       emulation_env : bool = False,
                       train_log_dto : TrainAgentLogDTO = None, eval_2 : bool = False):

    for episode in range(n_eval_episodes):
        if isinstance(env, SubprocVecEnv):
            infos = np.array([{constants.INFO_DICT.ATTACKER_NON_LEGAL_ACTIONS: env.attacker_initial_illegal_actions,
                               constants.INFO_DICT.DEFENDER_NON_LEGAL_ACTIONS: env.defender_initial_illegal_actions
                               } for i in range(env.num_envs)])
        elif isinstance(env, DummyVecEnv):
            infos = np.array([{constants.INFO_DICT.ATTACKER_NON_LEGAL_ACTIONS: env.envs[i].attacker_initial_illegal_actions,
                               constants.INFO_DICT.DEFENDER_NON_LEGAL_ACTIONS: env.envs[i].defender_initial_illegal_actions
                               } for i in range(env.num_envs)])
        for i in range(env.num_envs):
            if env_configs is not None:
                env_conf = env_configs[i]
            else:
                env_conf = env_config
            if isinstance(env, SubprocVecEnv):
                obs = env.eval_reset(idx=i)
            elif isinstance(env, DummyVecEnv):
                obs = env.envs[i].reset()
                env_conf = env.env_config(i)
                env_configs = env.env_configs()
            done = False
            state = None
            env_state = None
            attacker_episode_reward = 0.0
            defender_episode_reward = 0.0
            episode_length = 0
            while not done:
                if isinstance(env, DummyVecEnv):
                    env_state = env.envs[i].env_state
                    agent_state = env.envs[i].attacker_agent_state
                if isinstance(obs, list):
                    obs_attacker, obs_defender = obs[0]
                else:
                    obs_attacker, obs_defender = obs
                attacker_actions = None
                defender_actions = [None]
                if train_mode == train_mode.TRAIN_ATTACKER or train_mode == train_mode.SELF_PLAY:
                    attacker_actions, state = attacker_model.predict(np.array([obs_attacker]), state=state,
                                                                     deterministic=deterministic,
                                                                     infos=infos,
                                                                     env_config = env_conf,
                                                                     env_configs=env_configs, env=env, env_idx=i,
                                                                     env_state=env_state,
                                                                     attacker=True)
                if train_mode == train_mode.TRAIN_DEFENDER or train_mode == train_mode.SELF_PLAY:
                    defender_actions, state = defender_model.predict(np.array([obs_defender]), state=state,
                                                                     deterministic=deterministic,
                                                                     infos=infos,
                                                                     env_config=env_conf,
                                                                     env_configs=env_configs, env=env, env_idx=i,
                                                                     env_state=env_state,
                                                                     attacker=False)
                    if attacker_actions is None:
                        attacker_actions = np.array([None])
                defender_action = defender_actions[0]
                attacker_action = attacker_actions[0]
                action = (attacker_action, defender_action)
                # if emulation_env:
                #     print("taking eval step in emulation: {}".format(action))
                # print("taking eval step in emulation: {}, episode:{}/{}".format(action, episode, n_eval_episodes))
                if isinstance(env, SubprocVecEnv):
                    obs, reward, done, _info = env.eval_step(action, idx=i)
                elif isinstance(env, DummyVecEnv):
                    obs, reward, done, _info = env.envs[i].step(action)
                # print("eval step in emulation complete: {}, episode:{}/{}".format(action, episode, n_eval_episodes))
                # if emulation_env:
                #     print("eval step in emulation complete")
                attacker_reward, defender_reward = reward
                infos = [_info]
                attacker_episode_reward += attacker_reward
                defender_episode_reward += defender_reward
                episode_length += 1

            # Record episode metrics
            if not eval_2:
                train_log_dto.attacker_eval_episode_rewards.append(attacker_episode_reward)
                train_log_dto.defender_eval_episode_rewards.append(defender_episode_reward)
                train_log_dto.eval_episode_steps.append(episode_length)
                train_log_dto.eval_episode_flags.append(_info[constants.INFO_DICT.FLAGS])
                train_log_dto.eval_episode_caught.append(_info[constants.INFO_DICT.CAUGHT_ATTACKER])
                train_log_dto.eval_episode_early_stopped.append(_info[constants.INFO_DICT.EARLY_STOPPED])
                train_log_dto.eval_episode_successful_intrusion.append(_info[constants.INFO_DICT.SUCCESSFUL_INTRUSION])
                train_log_dto.eval_episode_snort_severe_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_REWARD])
                train_log_dto.eval_episode_snort_warning_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_REWARD])
                train_log_dto.eval_episode_snort_critical_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_REWARD])
                train_log_dto.eval_episode_var_log_baseline_rewards.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_REWARD])
                train_log_dto.eval_episode_step_baseline_rewards.append(_info[constants.INFO_DICT.STEP_BASELINE_REWARD])
                train_log_dto.eval_episode_snort_severe_baseline_steps.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_STEP])
                train_log_dto.eval_episode_snort_warning_baseline_steps.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_STEP])
                train_log_dto.eval_episode_snort_critical_baseline_steps.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_STEP])
                train_log_dto.eval_episode_var_log_baseline_steps.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_STEP])
                train_log_dto.eval_episode_step_baseline_steps.append(_info[constants.INFO_DICT.STEP_BASELINE_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_episode_snort_warning_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_episode_snort_critical_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_episode_var_log_baseline_caught_attacker.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_episode_step_baseline_caught_attacker.append(_info[constants.INFO_DICT.STEP_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_episode_snort_severe_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_episode_snort_warning_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_episode_snort_critical_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_episode_var_log_baseline_early_stopping.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_episode_step_baseline_early_stopping.append(_info[constants.INFO_DICT.STEP_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_episode_snort_severe_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_episode_snort_warning_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_episode_snort_critical_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_episode_var_log_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_episode_step_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.STEP_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_episode_flags_percentage.append(_info[constants.INFO_DICT.FLAGS] / env_conf.num_flags)
                train_log_dto.eval_attacker_action_costs.append(_info[constants.INFO_DICT.ATTACKER_COST])
                train_log_dto.eval_attacker_action_costs_norm.append(_info[constants.INFO_DICT.ATTACKER_COST_NORM])
                train_log_dto.eval_attacker_action_alerts.append(_info[constants.INFO_DICT.ATTACKER_ALERTS])
                train_log_dto.eval_attacker_action_alerts_norm.append(_info[constants.INFO_DICT.ATTACKER_ALERTS_NORM])
                train_log_dto.eval_episode_intrusion_steps.append(_info[constants.INFO_DICT.INTRUSION_STEP])
                train_log_dto.eval_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_optimal_defender_reward.append(_info[constants.INFO_DICT.OPTIMAL_DEFENDER_REWARD])
                train_log_dto.eval_defender_stops_remaining.append(_info[constants.INFO_DICT.DEFENDER_STOPS_REMAINING])
                train_log_dto.eval_defender_first_stop_step.append(_info[constants.INFO_DICT.DEFENDER_FIRST_STOP_STEP])
                train_log_dto.eval_defender_second_stop_step.append(_info[constants.INFO_DICT.DEFENDER_SECOND_STOP_STEP])
                train_log_dto.eval_defender_third_stop_step.append(_info[constants.INFO_DICT.DEFENDER_THIRD_STOP_STEP])
                train_log_dto.eval_defender_fourth_stop_step.append(_info[constants.INFO_DICT.DEFENDER_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_episode_snort_warning_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_episode_snort_critical_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_episode_var_log_baseline_first_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_episode_step_baseline_first_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_episode_snort_warning_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_episode_snort_critical_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_episode_var_log_baseline_second_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_episode_step_baseline_second_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_episode_snort_warning_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_episode_snort_critical_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_episode_var_log_baseline_third_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_episode_step_baseline_third_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_snort_warning_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_snort_critical_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_var_log_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_step_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_episode_snort_severe_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_episode_snort_warning_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_episode_snort_critical_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_episode_var_log_baseline_stops_remaining.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_episode_step_baseline_stops_remaining.append(_info[constants.INFO_DICT.STEP_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_optimal_stops_remaining.append(_info[constants.INFO_DICT.OPTIMAL_STOPS_REMAINING])
                train_log_dto.eval_optimal_first_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_FIRST_STOP_STEP])
                train_log_dto.eval_optimal_second_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_SECOND_STOP_STEP])
                train_log_dto.eval_optimal_third_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_THIRD_STOP_STEP])
                train_log_dto.eval_optimal_fourth_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_FOURTH_STOP_STEP])
                train_log_dto.eval_optimal_defender_episode_steps.append(_info[constants.INFO_DICT.OPTIMAL_DEFENDER_EPISODE_STEPS])
                train_log_dto.eval_update_env_specific_metrics(env_conf, _info, i)
            else:
                train_log_dto.attacker_eval_2_episode_rewards.append(attacker_episode_reward)
                train_log_dto.defender_eval_2_episode_rewards.append(defender_episode_reward)
                train_log_dto.eval_2_episode_steps.append(episode_length)
                train_log_dto.eval_2_episode_flags.append(_info[constants.INFO_DICT.FLAGS])
                train_log_dto.eval_2_episode_caught.append(_info[constants.INFO_DICT.CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_early_stopped.append(_info[constants.INFO_DICT.EARLY_STOPPED])
                train_log_dto.eval_2_episode_successful_intrusion.append(_info[constants.INFO_DICT.SUCCESSFUL_INTRUSION])
                train_log_dto.eval_2_episode_snort_severe_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_REWARD])
                train_log_dto.eval_2_episode_snort_warning_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_REWARD])
                train_log_dto.eval_2_episode_snort_critical_baseline_rewards.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_REWARD])
                train_log_dto.eval_2_episode_step_baseline_rewards.append(_info[constants.INFO_DICT.STEP_BASELINE_REWARD])
                train_log_dto.eval_2_episode_snort_severe_baseline_steps.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_STEP])
                train_log_dto.eval_2_episode_snort_warning_baseline_steps.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_STEP])
                train_log_dto.eval_2_episode_snort_critical_baseline_steps.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_STEP])
                train_log_dto.eval_2_episode_var_log_baseline_steps.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_STEP])
                train_log_dto.eval_2_episode_step_baseline_steps.append(_info[constants.INFO_DICT.STEP_BASELINE_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_snort_warning_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_snort_critical_baseline_caught_attacker.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_var_log_baseline_caught_attacker.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_step_baseline_caught_attacker.append(_info[constants.INFO_DICT.STEP_BASELINE_CAUGHT_ATTACKER])
                train_log_dto.eval_2_episode_snort_severe_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_2_episode_snort_warning_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_2_episode_snort_critical_baseline_early_stopping.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_2_episode_var_log_baseline_early_stopping.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_2_episode_step_baseline_early_stopping.append(_info[constants.INFO_DICT.STEP_BASELINE_EARLY_STOPPING])
                train_log_dto.eval_2_episode_snort_severe_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_episode_snort_warning_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_episode_snort_critical_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_episode_var_log_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_episode_step_baseline_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.STEP_BASELINE_UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_episode_var_log_baseline_rewards.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_REWARD])
                train_log_dto.eval_2_episode_flags_percentage.append(_info[constants.INFO_DICT.FLAGS] / env_conf.num_flags)
                train_log_dto.eval_2_attacker_action_costs.append(_info[constants.INFO_DICT.ATTACKER_COST])
                train_log_dto.eval_2_attacker_action_costs_norm.append(_info[constants.INFO_DICT.ATTACKER_COST_NORM])
                train_log_dto.eval_2_attacker_action_alerts.append(_info[constants.INFO_DICT.ATTACKER_ALERTS])
                train_log_dto.eval_2_attacker_action_alerts_norm.append(_info[constants.INFO_DICT.ATTACKER_ALERTS_NORM])
                train_log_dto.eval_2_episode_intrusion_steps.append(_info[constants.INFO_DICT.INTRUSION_STEP])
                train_log_dto.eval_2_uncaught_intrusion_steps.append(_info[constants.INFO_DICT.UNCAUGHT_INTRUSION_STEPS])
                train_log_dto.eval_2_optimal_defender_reward.append(_info[constants.INFO_DICT.OPTIMAL_DEFENDER_REWARD])
                train_log_dto.eval_2_defender_stops_remaining.append(_info[constants.INFO_DICT.DEFENDER_STOPS_REMAINING])
                train_log_dto.eval_2_defender_first_stop_step.append(_info[constants.INFO_DICT.DEFENDER_FIRST_STOP_STEP])
                train_log_dto.eval_2_defender_second_stop_step.append(_info[constants.INFO_DICT.DEFENDER_SECOND_STOP_STEP])
                train_log_dto.eval_2_defender_third_stop_step.append(_info[constants.INFO_DICT.DEFENDER_THIRD_STOP_STEP])
                train_log_dto.eval_2_defender_fourth_stop_step.append(_info[constants.INFO_DICT.DEFENDER_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_2_episode_snort_warning_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_2_episode_snort_critical_baseline_first_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_2_episode_var_log_baseline_first_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_2_episode_step_baseline_first_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_FIRST_STOP_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_2_episode_snort_warning_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_2_episode_snort_critical_baseline_second_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_2_episode_var_log_baseline_second_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_2_episode_step_baseline_second_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_SECOND_STOP_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_2_episode_snort_warning_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_2_episode_snort_critical_baseline_third_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_2_episode_var_log_baseline_third_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_2_episode_step_baseline_third_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_THIRD_STOP_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_snort_warning_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_snort_critical_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_var_log_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_step_baseline_fourth_stop_step.append(_info[constants.INFO_DICT.STEP_BASELINE_FOURTH_STOP_STEP])
                train_log_dto.eval_2_episode_snort_severe_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_SEVERE_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_2_episode_snort_warning_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_WARNING_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_2_episode_snort_critical_baseline_stops_remaining.append(_info[constants.INFO_DICT.SNORT_CRITICAL_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_2_episode_var_log_baseline_stops_remaining.append(_info[constants.INFO_DICT.VAR_LOG_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_2_episode_step_baseline_stops_remaining.append(_info[constants.INFO_DICT.STEP_BASELINE_STOPS_REMAINING])
                train_log_dto.eval_2_optimal_stops_remaining.append(_info[constants.INFO_DICT.OPTIMAL_STOPS_REMAINING])
                train_log_dto.eval_2_optimal_first_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_FIRST_STOP_STEP])
                train_log_dto.eval_2_optimal_second_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_SECOND_STOP_STEP])
                train_log_dto.eval_2_optimal_third_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_THIRD_STOP_STEP])
                train_log_dto.eval_2_optimal_fourth_stop_step.append(_info[constants.INFO_DICT.OPTIMAL_FOURTH_STOP_STEP])
                train_log_dto.eval_2_optimal_defender_episode_steps.append(_info[constants.INFO_DICT.OPTIMAL_DEFENDER_EPISODE_STEPS])
                train_log_dto.eval_2_update_env_specific_metrics(env_conf, _info, i)
            if isinstance(env, SubprocVecEnv):
                obs = env.eval_reset(idx=i)
            elif isinstance(env, DummyVecEnv):
                obs = env.envs[i].reset()
                env_conf = env.env_config(i)
                env_configs = env.env_configs()
    return train_log_dto
