from typing import List, Dict, Tuple, Union, Optional
import math
import random
from csle_common.dao.training.policy import Policy
from csle_common.dao.training.agent_type import AgentType
from csle_common.dao.simulation_config.state import State
from csle_common.dao.simulation_config.state_type import StateType
from csle_common.dao.training.player_type import PlayerType
from csle_common.dao.simulation_config.action import Action
from csle_common.dao.training.experiment_config import ExperimentConfig


class MultiThresholdStoppingPolicy(Policy):
    """
    A multi-threshold stopping policy
    """

    def __init__(self, theta, simulation_name: str, L: int, states : List[State], player_type: PlayerType,
                 actions: List[Action], experiment_config: Optional[ExperimentConfig], avg_R: float,
                 agent_type: AgentType, opponent_strategy: Optional["MultiThresholdStoppingPolicy"] = None):
        """
        Initializes the policy

        :param theta: the threshold vector
        :param simulation_name: the simulation name
        :param attacker: whether it is an attacker or not
        :param L: the number of stop actions
        :param states: list of states (required for computing stage policies)
        :param actions: list of actions
        :param experiment_config: the experiment configuration used for training the policy
        :param avg_R: the average reward of the policy when evaluated in the simulation
        :param agent_type: the agent type
        :param opponent_strategy: optionally an opponent strategy
        """
        super(MultiThresholdStoppingPolicy, self).__init__(agent_type=agent_type, player_type=player_type)
        self.theta = theta
        self.id = -1
        self.simulation_name = simulation_name
        self.L = L
        self.states = states
        self.actions = actions
        self.experiment_config = experiment_config
        self.avg_R = avg_R
        self.opponent_strategy = opponent_strategy

    def action(self, o: List[float]) -> int:
        """
        Multi-threshold stopping policy

        :param o: the current observation
        :return: the selected action
        """
        if not self.player_type == PlayerType.ATTACKER:
            a, _ = self._defender_action(o=o)
            return a
        else:
            return self._attacker_action(o=o)

    def _attacker_action(self, o) -> int:
        """
        Multi-threshold stopping policy of the attacker

        :param o: the input observation
        :return: the selected action (int)
        """
        s = o[2]
        b1 = o[1]
        l = int(o[0])
        theta_val = self.theta[int(s*self.L + l-1)]
        a1, prob = self.opponent_strategy._defender_action(o=o)
        if a1 == 1:
            defender_stopping_prob = prob
        else:
            defender_stopping_prob = 1-prob
        # defender_stopping_prob = b1


        # defender_stopping_prob = b1
        # def_stop_prob = 0
        # defender_stopping_prob = 0
        # b1 = defender_stopping_prob
        threshold = MultiThresholdStoppingPolicy.sigmoid(theta_val)
        if s == 0:
            a, _ = MultiThresholdStoppingPolicy.smooth_threshold_action_selection(
                threshold=threshold, b1=defender_stopping_prob, threshold_action=0, alternative_action=1, k=-20)
        elif s == 1:
            a, _ = MultiThresholdStoppingPolicy.smooth_threshold_action_selection(
                threshold=threshold, b1=defender_stopping_prob, threshold_action=1, alternative_action=0, k=-20)
        else:
            raise ValueError(f"Invalid state: {s}, valid states are: 0 and 1")
        # print(f"a2:{a}, s: {s}, thresh:{threshold}, prob: {defender_stopping_prob}")
        return a

    def stage_policy(self, o: Union[List[Union[int, float]], int, float]) -> List[List[float]]:
        """
        Gets the stage policy, i.e a |S|x|A| policy

        :param o: the latest observation
        :return: the |S|x|A| stage policy
        """
        b1 = o[1]
        l = int(o[0])
        threshold = MultiThresholdStoppingPolicy.sigmoid(self.theta[l - 1])
        if not self.player_type == PlayerType.ATTACKER:
            stage_policy = []
            for _ in self.states:
                stopping_probability = MultiThresholdStoppingPolicy.stopping_probability(b1=b1, threshold=threshold, k=-20)
                stage_policy.append([1-stopping_probability, stopping_probability])
            return stage_policy
        else:
            stage_policy = []
            a1, defender_stopping_probability = self.opponent_strategy._defender_action(o=o)
            if a1 == 0:
                defender_stopping_probability = 1-defender_stopping_probability
            for s in self.states:
                if s.state_type != StateType.TERMINAL:
                    theta_val = self.theta[s.id*self.L + l-1]
                    threshold = MultiThresholdStoppingPolicy.sigmoid(theta_val)
                    threshold_action_probability = MultiThresholdStoppingPolicy.stopping_probability(
                        b1=defender_stopping_probability, threshold=threshold, k=-20)
                    if s.id == 1:
                        stage_policy.append([1-threshold_action_probability, threshold_action_probability])
                    elif s.id == 0:
                        stage_policy.append([threshold_action_probability, 1-threshold_action_probability])
                    else:
                        raise ValueError(f"Invalid state: {s.id}, valid states are: 0 and 1")
                else:
                    stage_policy.append([0.5, 0.5])
            return stage_policy

    def _defender_action(self, o) -> Tuple[int, float]:
        """
        Multi-threshold stopping policy of the defender

        :param o: the input observation
        :return: the selected action (int)
        """
        b1 = o[1]
        l = int(o[0])
        threshold = MultiThresholdStoppingPolicy.sigmoid(self.theta[l - 1])
        # a = 0
        # prob = 1
        # if b1 >= threshold:
        a, prob = MultiThresholdStoppingPolicy.smooth_threshold_action_selection(
            threshold=threshold, b1=b1, threshold_action=1, alternative_action=0)
        return a, prob

    @staticmethod
    def sigmoid(x) -> float:
        """
        The sigmoid function

        :param x: the input
        :return: sigmoid(x)
        """
        return 1/(1 + math.exp(-x))

    @staticmethod
    def inverse_sigmoid(y) -> float:
        """
        The inverse sigmoid function

        :param y: sigmoid(x)
        :return: sigmoid(x)^(-1)
        """
        return math.log(y/(1-y), math.e)

    @staticmethod
    def smooth_threshold_action_selection(threshold: float, b1: float, threshold_action: int = 1,
                                          alternative_action: int = 1, k=-20) -> Tuple[int, float]:
        """
        Selects the next action according to a smooth threshold function on the belief

        :param threshold: the threshold
        :param b1: the belief
        :param threshold_action: the action to select if the threshold is exceeded
        :param alternative_action: the alternative action to select if the threshold is not exceeded
        :return: the selected action and the probability
        """
        prob = MultiThresholdStoppingPolicy.stopping_probability(b1=b1, threshold=threshold, k=k)
        if random.uniform(0,1) >= prob:
            return alternative_action, 1-prob
        else:
            return threshold_action, prob

    @staticmethod
    def stopping_probability(b1, threshold, k=-20) -> float:
        """
        Returns the probability of stopping given a belief and a threshold

        :param b1: the belief
        :param threshold: the threshold
        :return: the stopping probability
        """
        if (1-round(b1,2)) == 0:
            return 1
        if round(b1,2) == 0:
            return 0
        if (threshold*(1-b1)) > 0 and (b1*(1-threshold))/(threshold*(1-b1)) > 0:
            try:
                return math.pow(1 + math.pow(((b1*(1-threshold))/(threshold*(1-b1))), k), -1)
            except:
                return 0
        else:
            return 0

    def to_dict(self) -> Dict[str, List[float]]:
        """
        :return: a dict representation of the policy
        """
        d = {}
        d["theta"] = self.theta
        d["id"] = self.id
        d["simulation_name"] = self.simulation_name
        d["thresholds"] = self.thresholds()
        d["states"] = list(map(lambda x: x.to_dict(), self.states))
        d["actions"] = list(map(lambda x: x.to_dict(), self.actions))
        d["player_type"] = self.player_type
        d["agent_type"] = self.agent_type
        d["L"] = self.L
        if self.experiment_config is not None:
            d["experiment_config"] = self.experiment_config.to_dict()
        else:
            d["experiment_config"] = None
        d["avg_R"] = self.avg_R
        return d

    @staticmethod
    def from_dict(d: Dict) -> "MultiThresholdStoppingPolicy":
        """
        Converst a dict representation of the object to an instance

        :param d: the dict to convert
        :return: the created instance
        """
        obj = MultiThresholdStoppingPolicy(
            theta=d["theta"], simulation_name=d["simulation_name"], L=d["L"],
            states=list(map(lambda x: State.from_dict(x), d["states"])), player_type=d["player_type"],
            actions=list(map(lambda x: Action.from_dict(x), d["actions"])),
            experiment_config=ExperimentConfig.from_dict(d["experiment_config"]), avg_R=d["avg_R"],
            agent_type=d["agent_type"])
        obj.id = d["id"]
        return obj

    def thresholds(self) -> List[float]:
        """
        :return: the thresholds
        """
        return list(map(lambda x: round(MultiThresholdStoppingPolicy.sigmoid(x), 3), self.theta))

    def __str__(self) -> str:
        """
        :return: a string representation of the object
        """
        return f"theta: {self.theta}, id: {self.id}, simulation_name: {self.simulation_name}, " \
               f"thresholds: {self.thresholds()}, player_type: {self.player_type}, " \
               f"L:{self.L}, states: {self.states}, agent_type: {self.agent_type}, actions: {self.actions}," \
               f"experiment_config: {self.experiment_config}, avg_R: {self.avg_R}"

