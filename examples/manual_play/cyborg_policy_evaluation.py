import numpy as np
from csle_common.metastore.metastore_facade import MetastoreFacade
from gym_csle_cyborg.dao.csle_cyborg_config import CSLECyborgConfig
from gym_csle_cyborg.dao.red_agent_type import RedAgentType
from gym_csle_cyborg.envs.cyborg_scenario_two_defender import CyborgScenarioTwoDefender

if __name__ == '__main__':
    ppo_policy = MetastoreFacade.get_ppo_policy(id=1)
    config = CSLECyborgConfig(
        gym_env_name="csle-cyborg-scenario-two-v1", scenario=2, baseline_red_agents=[RedAgentType.B_LINE_AGENT],
        maximum_steps=100, red_agent_distribution=[1.0], reduced_action_space=True, decoy_state=True,
        scanned_state=True, decoy_optimization=False, cache_visited_states=False)
    csle_cyborg_env = CyborgScenarioTwoDefender(config=config)
    num_evaluations = 10000
    max_horizon = 25
    returns = []
    print("Starting policy evaluation")
    for i in range(num_evaluations):
        done = False
        o, _ = csle_cyborg_env.reset()
        R = 0
        t = 0
        while not done and t < max_horizon:
            a = ppo_policy.action(o=o)
            o, r, done, _, info = csle_cyborg_env.step(a)
            # print(f"a: {csle_cyborg_env.action_id_to_type_and_host[a]}")
            R += r
            t += 1
        returns.append(R)
        print(f"{i}/{num_evaluations}, avg R: {np.mean(returns)}")
