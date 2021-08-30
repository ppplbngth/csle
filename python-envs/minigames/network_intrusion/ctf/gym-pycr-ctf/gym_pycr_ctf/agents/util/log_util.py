import numpy as np
import sys
from gym_pycr_ctf.agents.config.agent_config import AgentConfig
from gym_pycr_ctf.dao.agent.train_mode import TrainMode
from gym_pycr_ctf.dao.agent.train_agent_log_dto import TrainAgentLogDTO
from gym_pycr_ctf.dao.agent.attacker_train_agent_log_dto_avg import AttackerTrainAgentLogDTOAvg
from gym_pycr_ctf.dao.agent.defender_train_agent_log_dto_avg import DefenderTrainAgentLogDTOAvg


class LogUtil:
    """
    Utility class for logging training progress
    """

    @staticmethod
    def log_metrics_attacker(train_log_dto: TrainAgentLogDTO, eps: float = None, eval: bool = False,
                             env=None, env_2 = None, attacker_agent_config : AgentConfig = None,
                             tensorboard_writer = None) -> TrainAgentLogDTO:
        """
        Logs average metrics for the last <self.config.log_frequency> episodes

        :param train_log_dto: DTO with the information to log
        :param eps: machine eps
        :param eval: flag whether it is evaluation or not
        :param env: the training env
        :param env_2: the evaluation env
        :param attacker_agent_config: the agent config of the attacker
        :param tensorboard_writer: the tensorobard writer
        :return: updated train log dto
        """
        avg_log_dto = AttackerTrainAgentLogDTOAvg(train_log_dto=train_log_dto,
                                                  attacker_agent_config=attacker_agent_config,
                                                  env=env, env_2=env_2, eval=eval)
        tensorboard_data_dto = AttackerTrainAgentLogDTOAvg.to_tensorboard_dto(
            avg_log_dto=avg_log_dto, eps=eps, tensorboard_writer=tensorboard_writer)
        log_str = tensorboard_data_dto.log_str_attacker()
        attacker_agent_config.logger.info(log_str)
        print(log_str)
        sys.stdout.flush()
        if attacker_agent_config.tensorboard:
            tensorboard_data_dto.log_tensorboard_attacker()

        train_log_dto = avg_log_dto.update_result()

        return train_log_dto


    @staticmethod
    def log_metrics_defender(train_log_dto: TrainAgentLogDTO, eps: float = None, eval: bool = False,
                             env=None, env_2 = None, defender_agent_config : AgentConfig = None,
                             tensorboard_writer = None, train_mode: TrainMode = TrainMode.TRAIN_ATTACKER) \
            -> TrainAgentLogDTO:
        """
        Logs average metrics for the last <self.config.log_frequency> episodes

        :param train_log_dto: DTO with the information to log
        :param eps: machine eps
        :param eval: flag whether it is evaluation or not
        :param env: the training env
        :param env_2: the eval env
        :param defender_agent_config: the agent config of the defender
        :param tensorboard_writer: the tensorboard writer
        :param train_mode: the training mode
        :return: updated train logs dto
        """
        avg_log_dto = DefenderTrainAgentLogDTOAvg(train_log_dto=train_log_dto,
                                                  defender_agent_config=defender_agent_config,
                                                  env=env, env_2=env_2, eval=eval, train_mode=train_mode)
        tensorboard_data_dto = DefenderTrainAgentLogDTOAvg.to_tensorboard_dto(
            avg_log_dto=avg_log_dto, eps=eps, tensorboard_writer=tensorboard_writer)
        log_str = tensorboard_data_dto.log_str_defender()
        defender_agent_config.logger.info(log_str)
        print(log_str)
        sys.stdout.flush()
        if defender_agent_config.tensorboard:
            tensorboard_data_dto.log_tensorboard_defender()

        train_log_dto = avg_log_dto.update_result()

        return train_log_dto