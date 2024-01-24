import io
import random

import numpy as np
from collections import Counter
from csle_common.metastore.metastore_facade import MetastoreFacade
from gym_csle_cyborg.dao.csle_cyborg_config import CSLECyborgConfig
from gym_csle_cyborg.dao.red_agent_type import RedAgentType
from gym_csle_cyborg.envs.cyborg_scenario_two_defender import CyborgScenarioTwoDefender
from gym_csle_cyborg.util.cyborg_env_util import CyborgEnvUtil
import csle_agents.constants.constants as constants
import json


def get_position(cyborg_hostname_values, state_vector, hostnames):
    access_values = []
    for i in range(len(list(cyborg_hostname_values.keys()))):
        access_state = state_vector[i][2]
        if access_state in [1, 2]:
            access_values.append(cyborg_hostname_values[hostnames[i]])
        else:
            access_values.append(0)
    position_idx = np.argmax(access_values)
    return position_idx


def get_target(attacker_action, ip_to_host_map, attacker_targets):
    if hasattr(attacker_action, 'hostname'):
        target = attacker_action.hostname
    elif hasattr(attacker_action, 'subnet'):
        target = str(attacker_action.subnet)
    elif hasattr(attacker_action, 'ip_address'):
        target = ip_to_host_map[str(attacker_action.ip_address)]
    else:
        raise ValueError(f"Action: {attacker_action} not recognized")
    target_idx = attacker_targets.index(target)
    return target_idx


def update_model(attacker_model, target, position, access, red_action):
    if position not in attacker_model["target_given_position_and_access"]:
        attacker_model["target_given_position_and_access"][position] = {}
    if access not in attacker_model["target_given_position_and_access"][position]:
        attacker_model["target_given_position_and_access"][position][access] = []
    attacker_model["target_given_position_and_access"][position][access].append(target)

    if target not in attacker_model["red_action_given_target_and_access"]:
        attacker_model["red_action_given_target_and_access"][target] = {}
    if access not in attacker_model["red_action_given_target_and_access"][target]:
        attacker_model["red_action_given_target_and_access"][target][access] = []
    attacker_model["red_action_given_target_and_access"][target][access].append(red_action)

    return attacker_model

def convert_samples_to_distribution(samples):
    """
    Converts a list of samples to a probability distribution

    :param samples: the list of samples
    :return: a dict with the sample values and their probabilities
    """
    cnt = Counter(samples)
    _sum = sum(cnt.values())
    return {k: v / _sum for k, v in cnt.items()}


def get_action_type(red_action, action_types):
    action_str_id = str(red_action).split(" ")[0]
    return action_types.index(action_str_id)


def get_access_state_lookup():
    lookup = {}
    s = 0
    for known in [0 ,1]:
        for scanned in [0,1]:
            for access in [0,1,2]:
                lookup[(known, scanned, access)] = s
                s+= 1
    return lookup

def get_access_state(host_state_vector, access_state_lookup):
    known = host_state_vector[0]
    scanned = host_state_vector[1]
    access = host_state_vector[2]
    return access_state_lookup[(known, scanned, access)]


if __name__ == '__main__':
    # ppo_policy = MetastoreFacade.get_ppo_policy(id=22)
    config = CSLECyborgConfig(
        gym_env_name="csle-cyborg-scenario-two-v1", scenario=2, baseline_red_agents=[RedAgentType.B_LINE_AGENT],
        maximum_steps=100, red_agent_distribution=[1.0], reduced_action_space=True, decoy_state=True,
        scanned_state=True, decoy_optimization=False, cache_visited_states=True)
    cyborg_hostname_values = {
        "Defender": 3,
        "Enterprise0": 3,
        "Enterprise1": 3,
        "Enterprise2": 4,
        "Op_Host0": 5,
        "Op_Host1": 5,
        "Op_Host2": 5,
        "Op_Server0": 6,
        "User0": 1,
        "User1": 2,
        "User2": 2,
        "User3": 2,
        "User4": 2
    }
    action_types = [
        "DiscoverRemoteSystems", "DiscoverNetworkServices", "ExploitRemoteService", "PrivilegeEscalate", "Impact"
    ]
    access_state_lookup = get_access_state_lookup()
    csle_cyborg_env = CyborgScenarioTwoDefender(config=config)
    # actions = [27, 28, 29, 30, 31, 32, 33, 34, 35]
    # a = random.choice(actions[0])
    counts = {}
    counts["target_given_position_and_access"] = {}
    counts["red_action_given_target_and_access"] = {}
    num_episodes = 1000
    for i in range(num_episodes):
        print(f"episode {i}/{num_episodes}")
        o, info = csle_cyborg_env.reset()
        subnets = csle_cyborg_env.get_subnetworks()
        attacker_targets = csle_cyborg_env.cyborg_hostnames + subnets
        ip_to_host = csle_cyborg_env.get_ip_to_host_mapping()
        done = False
        while not done:
            o, r, done, _, info = csle_cyborg_env.step(action=1)
            s = info[constants.ENV_METRICS.STATE]
            position = get_position(cyborg_hostname_values=cyborg_hostname_values,
                                    state_vector=CyborgEnvUtil.state_id_to_state_vector(state_id=s, observation=False),
                                    hostnames=csle_cyborg_env.cyborg_hostnames)
            red_action = csle_cyborg_env.get_last_action(agent="Red")
            red_action_type = get_action_type(red_action=red_action, action_types=action_types)
            target_idx = get_target(attacker_action=red_action, ip_to_host_map=ip_to_host,
                                    attacker_targets=attacker_targets)
            state_vector = CyborgEnvUtil.state_id_to_state_vector(state_id=s, observation=False)
            target_access_state = 0
            if target_idx < len(state_vector):
                target_access_state = get_access_state(host_state_vector=state_vector[target_idx],
                                                       access_state_lookup=access_state_lookup)
            counts = update_model(attacker_model=counts, target=target_idx, position=position,
                                  access=target_access_state, red_action=red_action_type)

    probability_model = {}
    probability_model["target_given_position_and_access"] = {}
    for k,v in counts["target_given_position_and_access"].items():
        probability_model["target_given_position_and_access"][int(k)] = {}
        for k2,v2 in v.items():
            probability_model["target_given_position_and_access"][int(k)][int(k2)] = {}
            distribution = convert_samples_to_distribution(samples=counts["target_given_position_and_access"][k][k2])
            for k3,v3 in distribution.items():
                probability_model["target_given_position_and_access"][int(k)][int(k2)][int(k3)] = float(v3)


    probability_model["red_action_given_target_and_access"] = {}
    for k,v in counts["red_action_given_target_and_access"].items():
        probability_model["red_action_given_target_and_access"][int(k)] = {}
        for k2,v2 in v.items():
            probability_model["red_action_given_target_and_access"][int(k)][int(k2)] = {}
            distribution = convert_samples_to_distribution(samples=counts["red_action_given_target_and_access"][k][k2])
            for k3,v3 in distribution.items():
                probability_model["red_action_given_target_and_access"][int(k)][int(k2)][int(k3)] = float(v3)

    print(probability_model)
    json_str = json.dumps(probability_model, indent=4, sort_keys=True)
    with io.open(f"/home/kim/attacker_model.json", 'w', encoding='utf-8') as f:
        f.write(json_str)
