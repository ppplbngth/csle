from typing import List, Dict
import math
import random
from csle_common.dao.training.policy import Policy
from csle_common.dao.training.agent_type import AgentType


class TSPSAPolicy(Policy):

    def __init__(self, theta):
        super(TSPSAPolicy, self).__init__(agent_type=AgentType.T_SPSA)
        self.theta = theta

    def action(self, o: List[float]) -> int:
        """
        Multi-threshold stopping policy

        :param o: the current observation
        :return: the selected action
        """
        b1 = o[1]
        l = int(o[0])
        threshold = TSPSAPolicy.sigmoid(self.theta[l-1])
        a = 0
        if b1 >= threshold:
            a = TSPSAPolicy.smooth_threshold_action_selection(threshold=threshold, b1=b1)
        return a

    @staticmethod
    def sigmoid(x) -> float:
        """
        The sigmoid function

        :param x:
        :return: sigmoid(x)
        """
        return 1/(1 + math.exp(-x))

    @staticmethod
    def smooth_threshold_action_selection(threshold: float, b1: float) -> int:
        """
        Selects the next action according to a smooth threshold function on the belief

        :param threshold: the threshold
        :param b1: the belief
        :return: the selected action
        """
        v=20
        prob = math.pow(1 + math.pow(((b1*(1-threshold))/(threshold*(1-b1))), -v), -1)
        if random.uniform(0,1) >= prob:
            return 0
        else:
            return 1

    def to_dict(self) -> Dict[str, List[float]]:
        """
        :return: a dict representation of the policy
        """
        d = {}
        d["theta"] = self.theta
        return d

    @staticmethod
    def from_dict(d: Dict) -> "TSPSAPolicy":
        """
        Converst a dict representation of the object to an instance

        :param d: the dict to convert
        :return: the created instance
        """
        obj = TSPSAPolicy(theta=d["theta"])
        return obj

    def thresholds(self) -> List[float]:
        """
        :return: the thresholds
        """
        return list(map(lambda x: TSPSAPolicy.sigmoid(x), self.theta))

    def __str__(self) -> str:
        """
        :return: a string representation of the object
        """
        return f"theta: {self.theta}"

