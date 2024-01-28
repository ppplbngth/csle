import random
from typing import Tuple, Dict, List, Any, Union
import numpy as np
import numpy.typing as npt
import gym_csle_cyborg.constants.constants as env_constants
from gym_csle_cyborg.dao.blue_agent_action_type import BlueAgentActionType
from gym_csle_cyborg.dao.red_agent_action_type import RedAgentActionType
from gym_csle_cyborg.dao.activity_type import ActivityType
from gym_csle_cyborg.dao.compromised_type import CompromisedType
from gym_csle_cyborg.util.cyborg_env_util import CyborgEnvUtil


class CyborgModelWrapper():

    def __init__(self, exploit_success_probabilities: npt.NDArray[Any], exploit_root_probabilities: npt.NDArray[Any],
                 exploit_user_probabilities: npt.NDArray[Any], activity_probabilities: npt.NDArray[Any],
                 compromise_probabilities: npt.NDArray[Any], maximum_steps: int):
        action_id_to_type_and_host, type_and_host_to_action_id = CyborgEnvUtil.get_action_dicts(
            scenario=2, reduced_action_space=True, decoy_optimization=False, decoy_state=True)
        self.action_id_to_type_and_host = action_id_to_type_and_host
        self.type_and_host_to_action_id = type_and_host_to_action_id
        self.maximum_steps = maximum_steps
        self.exploit_success_probabilities = exploit_success_probabilities
        self.exploit_root_probabilities = exploit_root_probabilities
        self.exploit_user_probabilities = exploit_user_probabilities
        self.activity_probabilities = activity_probabilities
        self.compromise_probabilities = compromise_probabilities
        self.initial_observation = CyborgModelWrapper.initial_obs_vector()
        self.s = CyborgModelWrapper.initial_state_vector()
        self.last_obs = CyborgModelWrapper.initial_obs_vector()
        self.hosts = CyborgEnvUtil.get_cyborg_hosts()
        self.host_compromised_costs = CyborgEnvUtil.get_host_compromised_costs()
        self.red_agent_action_types = CyborgEnvUtil.get_red_agent_action_types()
        self.cyborg_host_values = CyborgEnvUtil.get_cyborg_host_values()
        self.red_agent_jumps = [0, 1, 2, 2, 2, 2, 5, 5, 5, 5, 9, 9, 9, 12, 13]
        self.action_id_to_type_and_host = action_id_to_type_and_host
        self.decoy_action_types = CyborgEnvUtil.get_decoy_action_types(scenario=2)
        self.decoy_actions_per_host = CyborgEnvUtil.get_decoy_actions_per_host(scenario=2)
        self.op_server_restored = False
        self.red_agent_state = 0
        self.red_agent_target = 0
        self.t = 1
        self.red_action_targets = {}
        self.red_action_targets[self.red_agent_state] = self.red_agent_target
        self.scan_state = [0 for _ in self.hosts]
        self.next_target_fixed = False
        self.host_to_subnet = CyborgEnvUtil.cyborg_host_to_subnet()

    def step(self, action: int) -> Tuple[npt.NDArray[Any], float, bool, bool, Dict[str, Any]]:
        """
        Takes a step in the environment

        :param action: the defender action
        :return: (obs, reward, terminated, truncated, info)
        """
        defender_action_type, defender_action_host = self.action_id_to_type_and_host[action]
        defender_action_host_id = self.hosts.index(defender_action_host)
        if defender_action_type == BlueAgentActionType.RESTORE and \
                defender_action_host == env_constants.CYBORG.OP_SERVER0:
            self.op_server_restored = True
        self.red_action_targets[self.red_agent_state] = self.red_agent_target
        s_prime = self.apply_defender_action_to_state(s=self.s, defender_action_type=defender_action_type,
                                                      defender_action_host_id=defender_action_host_id,
                                                      decoy_action_types=self.decoy_action_types,
                                                      decoy_actions_per_host=self.decoy_actions_per_host)
        next_red_action_type = CyborgModelWrapper.get_red_agent_action_type_from_state(
            red_agent_state=self.red_agent_state)
        is_red_action_feasible = CyborgModelWrapper.is_red_action_feasible(red_agent_state=self.red_agent_state,
                                                                           s=s_prime,
                                                                           target_host_id=self.red_agent_target)
        exploit_successful = True
        decoy_state = s_prime[self.red_agent_target][env_constants.CYBORG.HOST_STATE_DECOY_IDX]
        if next_red_action_type == RedAgentActionType.EXPLOIT_REMOTE_SERVICE:
            rand_value = random.uniform(0, 1)
            exploit_successful = rand_value <= self.exploit_success_probabilities[self.red_agent_target][decoy_state]
        red_base_jump = self.red_agent_state == 12 and not is_red_action_feasible
        if red_base_jump:
            next_red_agent_state = 1
            next_red_agent_target = self.red_action_targets[next_red_agent_state]
        else:
            if is_red_action_feasible and exploit_successful:
                next_red_agent_state = (self.red_agent_state + 1) if self.red_agent_state < 14 else 14
                next_red_agent_target = CyborgModelWrapper.sample_next_red_agent_target(
                    red_agent_state=next_red_agent_state, red_agent_target=self.red_agent_target)
            else:
                next_red_agent_state = self.red_agent_jumps[self.red_agent_state]
                next_red_agent_target = self.red_action_targets[next_red_agent_state]

        if is_red_action_feasible:
            if next_red_action_type == RedAgentActionType.EXPLOIT_REMOTE_SERVICE:
                if exploit_successful:
                    exploit_access = CompromisedType.USER
                    if random.uniform(0, 1) <= self.exploit_root_probabilities[self.red_agent_target][decoy_state]:
                        exploit_access = CompromisedType.PRIVILEGED
                    s_prime = CyborgModelWrapper.apply_red_exploit(s=s_prime, exploit_access=exploit_access,
                                                                   target_host_id=self.red_agent_target)
            elif next_red_action_type == RedAgentActionType.DISCOVER_REMOTE_SYSTEMS:
                s_prime = CyborgModelWrapper.apply_red_network_scan(s=s_prime, target_subnetwork=self.red_agent_target)
            elif next_red_action_type == RedAgentActionType.DISCOVER_NETWORK_SERVICES:
                s_prime = CyborgModelWrapper.apply_red_host_scan(s=s_prime, target_host_id=self.red_agent_target)
            elif next_red_action_type == RedAgentActionType.PRIVILEGE_ESCALATE:
                s_prime = CyborgModelWrapper.apply_red_privilege_escalation(
                    s=s_prime, target_host_id=self.red_agent_target, red_agent_state=self.red_agent_state,
                    next_target_host_id=next_red_agent_target)
        self.s = s_prime
        self.red_agent_target = next_red_agent_target
        self.red_agent_state = next_red_agent_state

        obs, obs_tensor, scan_state = CyborgModelWrapper.generate_observation(
            s=s_prime, scan_state=self.scan_state, activity_probabilities=self.activity_probabilities,
            compromise_probabilities=self.compromise_probabilities, red_agent_action_type=next_red_action_type,
            red_agent_target=self.red_agent_target,
            decoy_action_types=self.decoy_action_types, decoy_actions_per_host=self.decoy_actions_per_host,
            defender_action_type=defender_action_type, defender_action_host_id=defender_action_host_id,
            last_obs=self.last_obs, host_to_subnet=self.host_to_subnet)
        self.scan_state = scan_state
        r = self.reward_function(defender_action_type=defender_action_type, red_action_type=next_red_action_type,
                                 red_success=(is_red_action_feasible and exploit_successful))
        self.s = s_prime
        self.last_obs = obs
        info = {}
        info[env_constants.ENV_METRICS.STATE] = CyborgEnvUtil.state_vector_to_state_id(state_vector=self.s,
                                                                                       observation=False)
        info[env_constants.ENV_METRICS.OBSERVATION] = CyborgEnvUtil.state_vector_to_state_id(state_vector=self.s,
                                                                                             observation=True)
        info[env_constants.ENV_METRICS.OBSERVATION_VECTOR] = obs
        done = False
        self.t += 1
        if self.t >= self.maximum_steps:
            done = True

        return np.array(obs_tensor), r, done, done, info

    def reset(self, seed: Union[None, int] = None, soft: bool = False, options: Union[Dict[str, Any], None] = None) \
            -> Tuple[npt.NDArray[Any], Dict[str, Any]]:
        """
        Resets the environment

        :param seed: the random seed
        :param soft: whether to do a soft reset or not
        :param options: reset options
        :return: the reset observation and info dict
        """
        self.s = self.initial_state_vector()
        self.op_server_restored = False
        self.red_agent_state = 0
        self.red_agent_target = 0
        self.t = 0
        self.red_action_targets = {}
        self.red_action_targets[self.red_agent_state] = self.red_agent_target
        obs_vec = self.initial_obs_vector()
        obs_tensor = self.initial_obs_tensor()
        self.last_obs = obs_vec
        info = {}
        info[env_constants.ENV_METRICS.STATE] = CyborgEnvUtil.state_vector_to_state_id(state_vector=self.s,
                                                                                       observation=False)
        info[env_constants.ENV_METRICS.OBSERVATION] = CyborgEnvUtil.state_vector_to_state_id(state_vector=obs_vec,
                                                                                             observation=True)
        info[env_constants.ENV_METRICS.OBSERVATION_VECTOR] = obs_vec
        return np.array(obs_tensor), info

    def reward_function(self, defender_action_type: BlueAgentActionType,
                        red_action_type: RedAgentActionType, red_success: bool) -> float:
        """
        The reward function

        :param defender_action_type: the type of the defender's action
        :param red_action_type: the type of the attacker's action
        :param red_success: a boolean flag indicating whether the red agent's action was successful
        :return: the reward
        """
        r = 0.0
        if defender_action_type == BlueAgentActionType.RESTORE:
            r -= 1
        for i in range(len(self.s)):
            access_state = self.s[i][env_constants.CYBORG.HOST_STATE_ACCESS_IDX]
            if access_state == CompromisedType.PRIVILEGED:
                r += self.host_compromised_costs[i]
        if red_action_type == RedAgentActionType.IMPACT and red_success and not self.op_server_restored:
            r -= 10
        return r

    def set_state(self, s: int) -> None:
        """
        Sets the state of the environment

        :param s: the id of the new state
        :return: None
        """
        self.s = CyborgEnvUtil.state_id_to_state_vector(state_id=s, observation=False)

    def get_observation_from_history(self, history: List[Any]) -> List[Any]:
        """
        Gets an observation from the observation history

        :param history: the observation history
        :return: the latest observation from the history
        """
        return history[-1]

    def is_state_terminal(self, state: int) -> bool:
        """
        Checks whether a given state is terminal or not

        :param state: the state id
        :return: True if terminal, else False
        """
        return False

    @staticmethod
    def initial_state_vector() -> List[List[int]]:
        """
        :return: gets the initial state vector
        """
        return [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                [0, 0, 0, 0], [1, 0, 2, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    @staticmethod
    def initial_obs_vector() -> List[List[int]]:
        """
        :return: gets the initial observation vector
        """
        return [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
                [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    @staticmethod
    def initial_obs_tensor() -> List[int]:
        """
        :return: gets the initial observation tensor
        """
        return [0] * 14 * 13

    @staticmethod
    def get_red_agent_action_type_from_state(red_agent_state: int) -> RedAgentActionType:
        """
        Gets the red agent action type from the red agent state

        :param red_agent_state: the state of the red agent
        :return: the type of red agent action
        """
        if red_agent_state == 0:
            return RedAgentActionType.DISCOVER_REMOTE_SYSTEMS
        elif red_agent_state == 1:
            return RedAgentActionType.DISCOVER_NETWORK_SERVICES
        elif red_agent_state == 2:
            return RedAgentActionType.EXPLOIT_REMOTE_SERVICE
        elif red_agent_state == 3:
            return RedAgentActionType.PRIVILEGE_ESCALATE
        elif red_agent_state == 4:
            return RedAgentActionType.DISCOVER_NETWORK_SERVICES
        elif red_agent_state == 5:
            return RedAgentActionType.EXPLOIT_REMOTE_SERVICE
        elif red_agent_state == 6:
            return RedAgentActionType.PRIVILEGE_ESCALATE
        elif red_agent_state == 7:
            return RedAgentActionType.DISCOVER_REMOTE_SYSTEMS
        elif red_agent_state == 8:
            return RedAgentActionType.DISCOVER_NETWORK_SERVICES
        elif red_agent_state == 9:
            return RedAgentActionType.EXPLOIT_REMOTE_SERVICE
        elif red_agent_state == 10:
            return RedAgentActionType.PRIVILEGE_ESCALATE
        elif red_agent_state == 11:
            return RedAgentActionType.DISCOVER_NETWORK_SERVICES
        elif red_agent_state == 12:
            return RedAgentActionType.EXPLOIT_REMOTE_SERVICE
        elif red_agent_state == 13:
            return RedAgentActionType.PRIVILEGE_ESCALATE
        elif red_agent_state == 14:
            return RedAgentActionType.IMPACT
        else:
            raise ValueError(f"Invalid attacker state: {red_agent_state}")

    @staticmethod
    def red_agent_state_to_target_distribution(red_agent_state: int, last_target: int = -1) -> List[float]:
        """
        Gets a distribution over the next target of the red agent based on its current state and previous target

        :param red_agent_state: the state of the red agent
        :param last_target: the previous target of the red agent
        :return: a distribution over the next target of the red agent
        """
        if red_agent_state == 0:
            return [1.0, 0, 0]
        elif red_agent_state == 1:
            return [0, 0, 0, 0, 0, 0, 0, 0, 0, 0.25, 0.25, 0.25, 0.25]
        elif red_agent_state in [2, 3, 5, 6, 9, 10, 12, 13, 14]:
            prob = [0] * 13
            prob[last_target] = 1
            return prob
        elif red_agent_state == 4:
            if last_target == 12 or last_target == 11:
                return [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            elif last_target == 9 or last_target == 10:
                return [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            else:
                raise ValueError(f"Invalid last target: {last_target}")
        elif red_agent_state == 7:
            return [0, 1.0, 0]
        elif red_agent_state == 8:
            return [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif red_agent_state == 11:
            return [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        else:
            raise ValueError(f"Invalid attacker state: {red_agent_state}")

    @staticmethod
    def is_red_action_feasible(red_agent_state: int, s: List[List[int]], target_host_id: int) -> bool:
        """
        Checks whether a given red agent is feasible or not

        :param red_agent_state: the red agent state
        :param s: the current state
        :param target_host_id: the target host id
        :return: True if feasible, else False
        """
        if red_agent_state == 0:
            return True
        elif red_agent_state == 1:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] == 1
        elif red_agent_state == 2:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_SCANNED_IDX] == 1
        elif red_agent_state == 3:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0
        elif red_agent_state == 4:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] == 1
        elif red_agent_state == 5:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_SCANNED_IDX] == 1
        elif red_agent_state == 6:
            return s[target_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0
        elif red_agent_state == 7:
            return (s[1][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0 or s[2][
                env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0)
        elif red_agent_state == 8:
            return s[3][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] == 1
        elif red_agent_state == 9:
            return s[3][env_constants.CYBORG.HOST_STATE_SCANNED_IDX] == 1
        elif red_agent_state == 10:
            return s[3][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0
        elif red_agent_state == 11:
            return s[3][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] == 2 and \
                   s[7][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] == 1
        elif red_agent_state == 12:
            return s[7][env_constants.CYBORG.HOST_STATE_SCANNED_IDX] == 1
        elif red_agent_state == 13:
            return s[7][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] > 0
        elif red_agent_state == 14:
            return s[7][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] == 2

    @staticmethod
    def apply_defender_action_to_state(s: List[List[int]], defender_action_type: BlueAgentActionType,
                                       defender_action_host_id: int, decoy_action_types: List[BlueAgentActionType],
                                       decoy_actions_per_host: List[List[BlueAgentActionType]]) -> List[List[int]]:
        """
        Applies a given defender action to the state

        :param s: the state to apply the action to
        :param defender_action_type: the type of the defender's action
        :param defender_action_host_id: the id of the host that the defender targets
        :param decoy_action_types: a list of decoy action types
        :param decoy_actions_per_host: a list of decoy action types per host
        :return: the updated state
        """
        if (defender_action_type in decoy_action_types
                and s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_DECOY_IDX] ==
                len(decoy_actions_per_host[defender_action_host_id])):
            defender_action_type = BlueAgentActionType.REMOVE
        if defender_action_type in decoy_action_types:
            s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_DECOY_IDX] = min(
                s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_DECOY_IDX] + 1,
                len(decoy_actions_per_host[defender_action_host_id]))
        elif defender_action_type == BlueAgentActionType.RESTORE:
            s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] = CompromisedType.NO.value
        elif defender_action_type == BlueAgentActionType.REMOVE:
            if s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] == CompromisedType.USER.value:
                s[defender_action_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] = CompromisedType.NO.value
        return s

    @staticmethod
    def sample_next_red_agent_target(red_agent_state: int, red_agent_target: int) -> int:
        """
        Samples the next red agent target

        :param red_agent_target: the current target of the red agent
        :param red_agent_state: the new state of the red agent
        :return: the next target host id of the red agent
        """
        target_dist = CyborgModelWrapper.red_agent_state_to_target_distribution(
            red_agent_state=red_agent_state, last_target=red_agent_target)
        next_target = np.random.choice(np.arange(0, len(target_dist)), p=target_dist)
        return next_target

    @staticmethod
    def apply_red_exploit(s: List[List[int]], exploit_access: CompromisedType, target_host_id: int) \
            -> List[List[int]]:
        """
        Applies a successful red exploit to the state

        :param s: the current state
        :param exploit_access: the access type of the exploit
        :param target_host_id: the targeted host id
        :return: the updated state
        """
        s[target_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] = \
            max(exploit_access.value, s[target_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] )
        return s

    @staticmethod
    def apply_red_network_scan(s: List[List[int]], target_subnetwork: int) -> List[List[int]]:
        """
        Applies a successful red scan of a subnetwork to the state

        :param s: the current state
        :param target_subnetwork: the targeted subnetwork id
        :return: the updated state
        """
        if target_subnetwork == 0:
            s[12][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[11][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[10][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[9][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
        if target_subnetwork == 1:
            s[0][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[1][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[2][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
            s[3][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
        return s

    @staticmethod
    def apply_red_host_scan(s: List[List[int]], target_host_id: int) -> List[List[int]]:
        """
        Applies a successful red host scan to the state

        :param s: the current state
        :param target_host_id: the targeted host id
        :return: the updated state
        """
        s[target_host_id][env_constants.CYBORG.HOST_STATE_SCANNED_IDX] = 1
        return s

    @staticmethod
    def apply_red_privilege_escalation(s: List[List[int]], target_host_id: int, red_agent_state: int,
                                       next_target_host_id: int) -> List[List[int]]:
        """
        Applies a successful red privilege escalation to the state

        :param s: the current state
        :param target_host_id: the targeted host id
        :param red_agent_state: the state of the red agent
        :param next_target_host_id: the id of the next targeted host
        :return: the updated state
        """
        s[target_host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX] = CompromisedType.PRIVILEGED.value
        if red_agent_state == 3 or red_agent_state == 10:
            s[next_target_host_id][env_constants.CYBORG.HOST_STATE_KNOWN_IDX] = 1
        return s

    @staticmethod
    def generate_observation(s: List[List[int]], scan_state: List[int], activity_probabilities: npt.NDArray[Any],
                             compromise_probabilities: npt.NDArray[Any], red_agent_action_type: int,
                             decoy_action_types: List[BlueAgentActionType],
                             decoy_actions_per_host: List[List[BlueAgentActionType]],
                             defender_action_type: BlueAgentActionType, defender_action_host_id: int,
                             red_agent_target: int, last_obs: List[List[int]], host_to_subnet: Dict[int, int]) \
            -> Tuple[List[List[int]], List[int], List[int]]:
        """
        Generates the defender observation based on the current state

        :param s: the current state
        :param scan_state: the current scanned state
        :param red_agent_target: the target of the red agent
        :param activity_probabilities: the activity observation probabilities
        :param compromise_probabilities: the compromise observation probabilities
        :param red_agent_action_type: the type of the red agent's action
        :param decoy_action_types: the list of decoy action types
        :param decoy_actions_per_host: the list of decoy actions per host
        :param defender_action_type: the action type of the defender
        :param defender_action_host_id: the id of the targeted host of the defender
        :param last_obs: the last observation
        :param host_to_subnet: a map from host id to subnet id
        :return: the latest observation, the one-hot encoded observation, and the updated scanned state
        """
        obs = []
        obs_tensor = []
        for host_id in range(len(s)):
            if host_id == 8:
                host_obs = [0, 0, 0, 0]
            else:
                analyze = 0
                if defender_action_host_id == host_id and defender_action_type == BlueAgentActionType.ANALYZE.value:
                    analyze = 1
                activity = ActivityType.NONE.value
                if host_id == red_agent_target and \
                        red_agent_action_type != RedAgentActionType.DISCOVER_REMOTE_SYSTEMS.value:
                    activity_distribution = activity_probabilities[host_id][red_agent_action_type]
                    if sum(activity_distribution) != 0:
                        activity = np.random.choice(np.arange(0, len(activity_distribution)), p=activity_distribution)
                host_access = s[host_id][env_constants.CYBORG.HOST_STATE_ACCESS_IDX]
                compromised_obs = last_obs[host_id]
                if red_agent_target == host_id or \
                        (red_agent_action_type == RedAgentActionType.DISCOVER_REMOTE_SYSTEMS.value
                         and red_agent_target == host_to_subnet[host_id]):
                    compromised_distribution = compromise_probabilities[host_id][host_access][analyze]
                    if sum(compromised_distribution) == 0:
                        compromised_obs =CompromisedType.NO.value
                    else:
                        compromised_obs = np.random.choice(np.arange(0, len(compromised_distribution)),
                                                           p=compromised_distribution)
                host_decoy_state = s[host_id][env_constants.CYBORG.HOST_STATE_DECOY_IDX]
                if activity == ActivityType.SCAN:
                    scan_state = [1 if x == 2 else x for x in scan_state]
                    scan_state[host_id] = 2
                host_obs = [activity, scan_state[host_id], compromised_obs, host_decoy_state]
            obs.append(host_obs)
            obs_tensor.extend(CyborgModelWrapper.host_obs_one_hot_encoding(
                host_obs=host_obs, decoy_action_types=decoy_action_types,
                decoy_actions_per_host=decoy_actions_per_host, host_id=host_id))
        return obs, obs_tensor, scan_state

    @staticmethod
    def host_obs_one_hot_encoding(host_obs: List[int], decoy_action_types: List[BlueAgentActionType],
                                  decoy_actions_per_host: List[List[BlueAgentActionType]], host_id: int) -> List[int]:
        """
        Gets a one-hot encoded version of a host observation

        :param host_obs: the host observation
        :param decoy_action_types: the list of decoy action types
        :param decoy_actions_per_host: the list of decoy action types per host
        :param host_id: the id of the host
        :return: the one hot encoded observation vector
        """
        one_hot_encoded_vector = []
        if host_obs[0] == ActivityType.NONE:
            one_hot_encoded_vector.extend([0, 0])
        elif host_obs[0] == ActivityType.SCAN:
            one_hot_encoded_vector.extend([1, 0])
        elif host_obs[0] == ActivityType.EXPLOIT:
            one_hot_encoded_vector.extend([1, 1])
        if host_obs[2] == CompromisedType.NO:
            one_hot_encoded_vector.extend([0, 0])
        elif host_obs[2] == CompromisedType.USER:
            one_hot_encoded_vector.extend([0, 1])
        elif host_obs[2] == CompromisedType.PRIVILEGED:
            one_hot_encoded_vector.extend([1, 1])
        elif host_obs[2] == CompromisedType.UNKNOWN:
            one_hot_encoded_vector.extend([1, 0])
        if host_obs[1] == 0:
            one_hot_encoded_vector.extend([0, 0])
        elif host_obs[1] == 1:
            one_hot_encoded_vector.extend([0, 1])
        elif host_obs[1] == 2:
            one_hot_encoded_vector.extend([1, 1])
        decoy_obs = [0] * len(decoy_action_types)
        for j in range(host_obs[3]):
            decoy_obs[decoy_action_types.index(decoy_actions_per_host[host_id][j])] = 1
        one_hot_encoded_vector.extend(decoy_obs)
        return one_hot_encoded_vector

    def get_action_space(self) -> List[int]:
        """
        Gets the action space of the defender

        :return: a list of action ids
        """
        return list(self.action_id_to_type_and_host.keys())
