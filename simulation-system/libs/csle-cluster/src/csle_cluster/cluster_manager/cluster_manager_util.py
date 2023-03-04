from typing import Dict, Any, List, Tuple
import logging
from requests import get
import csle_common.constants.constants as constants
from csle_common.dao.emulation_config.emulation_env_config import EmulationEnvConfig
from csle_common.controllers.container_controller import ContainerController
from csle_common.dao.emulation_config.snort_managers_info import SnortIdsManagersInfo
from csle_common.dao.emulation_config.ossec_managers_info import OSSECIDSManagersInfo
from csle_common.dao.emulation_config.host_managers_info import HostManagersInfo
from csle_common.dao.emulation_config.kafka_managers_info import KafkaManagersInfo
from csle_common.dao.emulation_config.client_managers_info import ClientManagersInfo
from csle_common.dao.emulation_config.traffic_managers_info import TrafficManagersInfo
from csle_common.dao.emulation_config.elk_managers_info import ELKManagersInfo
from csle_common.dao.emulation_config.ryu_managers_info import RyuManagersInfo
from csle_common.dao.emulation_config.docker_stats_managers_info import DockerStatsManagersInfo
from csle_common.dao.emulation_config.emulation_execution_info import EmulationExecutionInfo
from csle_common.dao.emulation_config.emulation_execution import EmulationExecution
from csle_common.controllers.emulation_env_controller import EmulationEnvController
from csle_common.util.general_util import GeneralUtil
import csle_collector.client_manager.client_manager_pb2
import csle_collector.traffic_manager.traffic_manager_pb2
import csle_collector.docker_stats_manager.docker_stats_manager_pb2
import csle_collector.elk_manager.elk_manager_pb2
import csle_collector.snort_ids_manager.snort_ids_manager_pb2
import csle_collector.ossec_ids_manager.ossec_ids_manager_pb2
import csle_collector.kafka_manager.kafka_manager_pb2
import csle_collector.ryu_manager.ryu_manager_pb2
import csle_collector.host_manager.host_manager_pb2
import csle_cluster.cluster_manager.cluster_manager_pb2 as cluster_manager_pb2
import csle_cluster.constants.constants as cluster_constants


class ClusterManagerUtil:
    """
    Class with utility functions related to the cluster manager
    """

    @staticmethod
    def convert_traffic_dto_to_traffic_manager_info_dto(
            traffic_dto: csle_collector.traffic_manager.traffic_manager_pb2.TrafficDTO) -> \
            cluster_manager_pb2.TrafficManagerInfoDTO:
        """
        Converts a TrafficDTO to a TrafficManagerInfoDTO

        :param traffic_dto: the DTO to convert
        :return: the converted DTO
        """
        if traffic_dto is None:
            return ClusterManagerUtil.get_empty_traffic_manager_info_dto()
        else:
            return cluster_manager_pb2.TrafficManagerInfoDTO(running=traffic_dto.running, script=traffic_dto.script)

    @staticmethod
    def get_empty_traffic_manager_info_dto() -> cluster_manager_pb2.TrafficManagerInfoDTO:
        """
        :return: an empty TrafficManagersInfoDTO
        """
        return cluster_manager_pb2.TrafficManagerInfoDTO(running=False, script="")

    @staticmethod
    def get_empty_traffic_managers_info_dto() -> cluster_manager_pb2.TrafficManagersInfoDTO:
        """
        :return: an empty TrafficManagersInfoDTO
        """
        return cluster_manager_pb2.TrafficManagersInfoDTO(ips=[], ports=[], emulationName="", executionId=-1,
                                                          trafficManagersRunning=[], trafficManagersStatuses=[])

    @staticmethod
    def get_empty_client_managers_info_dto() -> cluster_manager_pb2.ClientManagersInfoDTO:
        """
        :return: an empty ClientManagersInfoDTO
        """
        return cluster_manager_pb2.ClientManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId=-1, clientManagersRunning=[],
            clientManagersStatuses=[])

    @staticmethod
    def get_empty_get_num_clients_dto() -> cluster_manager_pb2.GetNumActiveClientsMsg:
        """
        :return: an empty GetNumClientsDTO
        """
        return cluster_manager_pb2.GetNumClientsDTO(num_clients=0, client_process_active=False, producer_active=False,
                                                    clients_time_step_len_seconds=0, producer_time_step_len_seconds=0)

    @staticmethod
    def convert_client_dto_to_get_num_clients_dto(
            clients_dto: csle_collector.client_manager.client_manager_pb2.ClientsDTO) -> \
            cluster_manager_pb2.GetNumActiveClientsMsg:
        """
        Converts a clients DTO to a GetNumClientsDTO

        :param clients_dto: the clients DTO to convert
        :return: the converted DTO
        """
        if clients_dto is None:
            return ClusterManagerUtil.get_empty_num_clients_dto()
        return cluster_manager_pb2.GetNumClientsDTO(
            num_clients=clients_dto.num_clients,
            client_process_active=clients_dto.client_process_active,
            producer_active=clients_dto.producer_active,
            clients_time_step_len_seconds=clients_dto.clients_time_step_len_seconds,
            producer_time_step_len_seconds=clients_dto.producer_time_step_len_seconds
        )

    @staticmethod
    def node_status_dto_to_dict(node_status_dto: cluster_manager_pb2.NodeStatusDTO) -> Dict[str, Any]:
        """
        Converts a NodeStatusDTO to a dict

        :param node_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ip"] = node_status_dto.ip
        d["leader"] = node_status_dto.leader
        d["cAdvisorRunning"] = node_status_dto.cAdvisorRunning
        d["prometheusRunning"] = node_status_dto.prometheusRunning
        d["grafanaRunning"] = node_status_dto.grafanaRunning
        d["pgAdminRunning"] = node_status_dto.pgAdminRunning
        d["nginxRunning"] = node_status_dto.nginxRunning
        d["flaskRunning"] = node_status_dto.flaskRunning
        d["dockerStatsManagerRunning"] = node_status_dto.dockerStatsManagerRunning
        d["nodeExporterRunning"] = node_status_dto.nodeExporterRunning
        d["postgreSQLRunning"] = node_status_dto.postgreSQLRunning
        d["dockerEngineRunning"] = node_status_dto.dockerEngineRunning
        return d

    @staticmethod
    def service_status_dto_to_dict(node_status_dto: cluster_manager_pb2.ServiceStatusDTO) -> Dict[str, Any]:
        """
        Converts a ServiceStatusDTO to a dict

        :param node_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["running"] = node_status_dto.running
        return d

    @staticmethod
    def logs_dto_to_dict(logs_dto: cluster_manager_pb2.LogsDTO) -> Dict[str, Any]:
        """
        Converts a LogsDTO to a dict

        :param logs_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["logs"] = list(logs_dto.logs)
        return d

    @staticmethod
    def get_num_clients_dto_to_dict(get_num_clients_dto: cluster_manager_pb2.GetNumClientsDTO) -> Dict[str, Any]:
        """
        Converts a GetNumClientsDTO to a dict

        :param get_num_clients_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["num_clients"] = get_num_clients_dto.num_clients
        d["client_process_active"] = get_num_clients_dto.client_process_active
        d["producer_active"] = get_num_clients_dto.producer_active
        d["clients_time_step_len_seconds"] = get_num_clients_dto.clients_time_step_len_seconds
        d["producer_time_step_len_seconds"] = get_num_clients_dto.producer_time_step_len_seconds
        return d

    @staticmethod
    def get_active_ips(emulation_env_config: EmulationEnvConfig) -> List[str]:
        """
        Gets the locally active ips for a given emulation

        :param emulation_env_config: the emulation configuration
        :return: the list of Ips
        """
        running_containers, stopped_containers = ContainerController.list_all_running_containers_in_emulation(
            emulation_env_config=emulation_env_config)
        active_ips = []
        for container in running_containers:
            active_ips = active_ips + container.get_ips()
        active_ips.append(constants.COMMON.LOCALHOST)
        active_ips.append(constants.COMMON.LOCALHOST_127_0_0_1)
        active_ips.append(constants.COMMON.LOCALHOST_127_0_1_1)
        return active_ips

    @staticmethod
    def client_managers_info_dto_to_dict(clients_managers_info_dto: cluster_manager_pb2.ClientManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a ClientManagersInfoDTO to a dict

        :param clients_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(clients_managers_info_dto.ips)
        d["ports"] = list(clients_managers_info_dto.ports)
        d["emulationName"] = clients_managers_info_dto.emulationName
        d["executionId"] = clients_managers_info_dto.executionId
        d["clientManagersRunning"] = list(clients_managers_info_dto.clientManagersRunning)
        d["clientManagersRunning"] = list(map(lambda x: ClusterManagerUtil.get_num_clients_dto_to_dict(x),
                                              list(clients_managers_info_dto.clientManagersRunning)))
        return d

    @staticmethod
    def traffic_manager_info_dto_to_dict(traffic_manager_info_dto: cluster_manager_pb2.TrafficManagerInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a TrafficManagerInfoDTO to a dict

        :param traffic_manager_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["running"] = traffic_manager_info_dto.running
        d["script"] = traffic_manager_info_dto.script
        return d

    @staticmethod
    def traffic_managers_info_dto_to_dict(traffic_managers_info_dto: cluster_manager_pb2.TrafficManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a TrafficManagersInfoDTO to a dict

        :param traffic_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(traffic_managers_info_dto.ips)
        d["ports"] = list(traffic_managers_info_dto.ports)
        d["trafficManagersRunning"] = list(traffic_managers_info_dto.trafficManagersRunning)
        d["trafficManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.traffic_manager_info_dto_to_dict(x),
                                                list(traffic_managers_info_dto.trafficManagersStatuses)))
        d["emulationName"] = traffic_managers_info_dto.emulationName
        d["executionId"] = traffic_managers_info_dto.executionId
        return d

    @staticmethod
    def docker_stats_monitor_status_dto_to_dict(
            docker_stats_managers_info_dto: cluster_manager_pb2.DockerStatsMonitorStatusDTO) -> Dict[str, Any]:
        """
        Converts a DockerStatsMonitorStatusDTO to a dict

        :param docker_stats_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["num_monitors"] = list(docker_stats_managers_info_dto.num_monitors)
        d["emulations"] = list(docker_stats_managers_info_dto.emulations)
        d["emulation_executions"] = list(docker_stats_managers_info_dto.emulation_executions)
        return d

    @staticmethod
    def docker_stats_managers_info_dto_to_dict(
            docker_stats_managers_info_dto: cluster_manager_pb2.DockerStatsManagersInfoDTO) -> Dict[str, Any]:
        """
        Converts a DockerStatsManagersInfoDTO to a dict

        :param docker_stats_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(docker_stats_managers_info_dto.ips)
        d["ports"] = list(docker_stats_managers_info_dto.ports)
        d["dockerStatsManagersRunning"] = list(docker_stats_managers_info_dto.dockerStatsManagersRunning)
        d["dockerStatsManagersStatuses"] = list(map(lambda x:
                                                    ClusterManagerUtil.docker_stats_monitor_status_dto_to_dict(x),
                                                    list(docker_stats_managers_info_dto.dockerStatsManagersStatuses)))
        d["emulationName"] = docker_stats_managers_info_dto.emulationName
        d["executionId"] = docker_stats_managers_info_dto.executionId
        return d

    @staticmethod
    def stopped_containers_dto_to_dict(stopped_containers_dto_to_dict: cluster_manager_pb2.StoppedContainersDTO) \
            -> Dict[str, Any]:
        """
        Converts a StoppedContainersDTO to a dict

        :param stopped_containers_dto_to_dict: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["stoppedContainers"] = list(map(lambda x: ClusterManagerUtil.docker_container_dto_to_dict(x),
                                          list(stopped_containers_dto_to_dict.stoppedContainers)))
        return d

    @staticmethod
    def docker_container_dto_to_dict(docker_container_dto_to_dict: cluster_manager_pb2.DockerContainerDTO) \
            -> Dict[str, Any]:
        """
        Converts a DockerContainerDTO to a dict

        :param docker_container_dto_to_dict: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["name"] = docker_container_dto_to_dict.name
        d["image"] = docker_container_dto_to_dict.image
        d["ip"] = docker_container_dto_to_dict.ip
        return d

    @staticmethod
    def running_emulations_dto_to_dict(running_emulations_dto: cluster_manager_pb2.RunningEmulationsDTO) \
            -> Dict[str, Any]:
        """
        Converts a RunningEmulationsDTO to a dict

        :param running_emulations_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["runningEmulations"] = list(running_emulations_dto.runningEmulations)
        return d

    @staticmethod
    def running_containers_dto_to_dict(running_containers_dto_to_dict: cluster_manager_pb2.RunningContainersDTO) \
            -> Dict[str, Any]:
        """
        Converts a RunningContainersDTO to a dict

        :param running_containers_dto_to_dict: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["runningContainers"] = list(map(lambda x: ClusterManagerUtil.docker_container_dto_to_dict(x),
                                          list(running_containers_dto_to_dict.stoppedContainers)))
        return d

    @staticmethod
    def docker_networks_dto_to_dict(docker_networks_dto: cluster_manager_pb2.DockerNetworksDTO) -> Dict[str, Any]:
        """
        Converts a DockerNetworksDTO to a dict

        :param docker_networks_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["networks"] = list(docker_networks_dto.networks)
        d["network_ids"] = list(docker_networks_dto.network_ids)
        return d

    @staticmethod
    def container_image_dto_to_dict(container_image_dto: cluster_manager_pb2.ContainerImageDTO) -> Dict[str, Any]:
        """
        Converts a ContainerImageDTO to a dict

        :param container_image_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["repoTags"] = list(container_image_dto.repoTags)
        d["created"] = list(container_image_dto.created)
        d["os"] = list(container_image_dto.os)
        d["architecture"] = list(container_image_dto.architecture)
        d["size"] = list(container_image_dto.size)
        return d

    @staticmethod
    def container_images_dtos_to_dict(container_images_dtos: cluster_manager_pb2.ContainerImagesDTO) -> Dict[str, Any]:
        """
        Converts a ContainerImagesDTO to a dict

        :param container_images_dtos: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["images"] = list(map(lambda x: ClusterManagerUtil.container_image_dto_to_dict(x),
                               list(container_images_dtos.images)))
        return d

    @staticmethod
    def convert_docker_stats_monitor_dto(
            monitor_dto: csle_collector.docker_stats_manager.docker_stats_manager_pb2.DockerStatsMonitorDTO) -> \
            cluster_manager_pb2.DockerStatsMonitorStatusDTO:
        """
        Converts a DockerStatsMonitorDTO to a DockerStatsMonitorStatusDTO

        :param monitor_dto: the DTO to convert
        :return: the converted DTO
        """
        if monitor_dto is None:
            return ClusterManagerUtil.get_empty_docker_stats_monitor_status_dto()
        return cluster_manager_pb2.DockerStatsMonitorStatusDTO(
            num_monitors=monitor_dto.num_monitors, emulations=monitor_dto.emulations,
            emulation_executions=monitor_dto.emulation_executions
        )

    @staticmethod
    def elk_status_dto_to_dict(elk_status_dto: cluster_manager_pb2.ElkStatusDTO) -> Dict[str, Any]:
        """
        Converts a ElkStatusDTO to a dict

        :param elk_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["elasticRunning"] = elk_status_dto.elasticRunning
        d["kibanaRunning"] = elk_status_dto.kibanaRunning
        d["logstashRunning"] = elk_status_dto.logstashRunning
        return d

    @staticmethod
    def elk_managers_info_dto_to_dict(elk_managers_info_dto: cluster_manager_pb2.ElkManagersInfoDTO) -> Dict[str, Any]:
        """
        Converts a ElkManagersInfoDTO to a dict

        :param elk_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(elk_managers_info_dto.ips)
        d["ports"] = list(elk_managers_info_dto.ports)
        d["elkManagersRunning"] = list(elk_managers_info_dto.elkManagersRunning)
        d["elkManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.elk_status_dto_to_dict(x),
                                            list(elk_managers_info_dto.elkManagersStatuses)))
        d["emulationName"] = elk_managers_info_dto.emulationName
        d["executionId"] = elk_managers_info_dto.executionId
        d["localKibanaPort"] = elk_managers_info_dto.localKibanaPort
        return d

    @staticmethod
    def convert_elk_dto(
            elk_dto: csle_collector.elk_manager.elk_manager_pb2.ElkDTO) -> cluster_manager_pb2.ElkStatusDTO:
        """
        Converts an ElkDTO to a ElkStatusDTO

        :param elk_dto: the DTO to convert
        :return: the converted DTO
        """
        if elk_dto is None:
            return ClusterManagerUtil.get_empty_elk_status_dto()
        return cluster_manager_pb2.ElkStatusDTO(
            elasticRunning=elk_dto.elasticRunning, kibanaRunning=elk_dto.kibanaRunning,
            logstashRunning=elk_dto.logstashRunning
        )

    @staticmethod
    def convert_snort_ids_monitor_dto_to_snort_ids_status_dto(
            snort_dto: csle_collector.snort_ids_manager.snort_ids_manager_pb2.SnortIdsMonitorDTO) -> \
            cluster_manager_pb2.SnortIdsStatusDTO:
        """
        Converts a SnortIdsMonitorDTO to a SnortIdsStatusDTO

        :param snort_dto: the DTO to convert
        :return: the converted DTO
        """
        if snort_dto is None:
            return ClusterManagerUtil.get_empty_snort_ids_status_dto()
        return cluster_manager_pb2.SnortIdsStatusDTO(monitor_running=snort_dto.monitor_running,
                                                     snort_ids_running=snort_dto.snort_ids_running)

    @staticmethod
    def convert_ossec_ids_monitor_dto_to_ossec_ids_status_dto(
            ossec_dto: csle_collector.ossec_ids_manager.ossec_ids_manager_pb2.OSSECIdsMonitorDTO) -> \
            cluster_manager_pb2.OSSECIdsStatusDTO:
        """
        Converts a OSSECIdsMonitorDTO to a OSSECIdsStatusDTO

        :param ossec_dto: the DTO to convert
        :return: the converted DTO
        """
        if ossec_dto is None:
            return ClusterManagerUtil.get_empty_ossec_ids_status_dto()
        return cluster_manager_pb2.OSSECIdsStatusDTO(monitor_running=ossec_dto.monitor_running,
                                                     ossec_ids_running=ossec_dto.ossec_ids_running)

    @staticmethod
    def convert_kafka_dto_to_kafka_status_dto(
            kafka_dto: csle_collector.kafka_manager.kafka_manager_pb2.KafkaDTO) -> cluster_manager_pb2.KafkaStatusDTO:
        """
        Converts a KafkaDTO to a KafkaStatusDTO

        :param kafka_dto: the DTO to convert
        :return: the converted DTO
        """
        if kafka_dto is None:
            return ClusterManagerUtil.get_empty_kafka_dto()
        return cluster_manager_pb2.KafkaStatusDTO(running=kafka_dto.running, topics=kafka_dto.topics)

    @staticmethod
    def convert_ryu_dto_to_kafka_status_dto(
            ryu_dto: csle_collector.ryu_manager.ryu_manager_pb2.RyuDTO) -> cluster_manager_pb2.RyuManagerStatusDTO:
        """
        Converts a RyuDTO to a RyuManagerStatusDTO

        :param ryu_dto: the DTO to convert
        :return: the converted DTO
        """
        if ryu_dto is None:
            return ClusterManagerUtil.get_empty_ryu_manager_status_dto()
        return cluster_manager_pb2.RyuManagerStatusDTO(
            ryu_running=ryu_dto.ryu_running, monitor_running=ryu_dto.monitor_running, port=ryu_dto.port,
            web_port=ryu_dto.web_port, controller=ryu_dto.controller, kafka_ip=ryu_dto.kafka_ip,
            kafka_port=ryu_dto.kafka_port, time_step_len=ryu_dto.time_step_len)

    @staticmethod
    def snort_ids_status_dto_to_dict(snort_ids_status_dto: cluster_manager_pb2.SnortIdsStatusDTO) -> Dict[str, Any]:
        """
        Converts a SnortIdsStatusDTO to a dict

        :param snort_ids_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["monitor_running"] = snort_ids_status_dto.monitor_running
        d["snort_ids_running"] = snort_ids_status_dto.snort_ids_running
        return d

    @staticmethod
    def ossec_ids_status_dto_to_dict(ossec_ids_status_dto: cluster_manager_pb2.OSSECIdsStatusDTO) -> Dict[str, Any]:
        """
        Converts a OSSECIdsStatusDTO to a dict

        :param ossec_ids_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["monitor_running"] = ossec_ids_status_dto.monitor_running
        d["ossec_ids_running"] = ossec_ids_status_dto.ossec_ids_running
        return d

    @staticmethod
    def snort_ids_monitor_thread_statuses_dto_to_dict(
            snort_ids_monitor_thread_statuses_dto: cluster_manager_pb2.SnortIdsMonitorThreadStatusesDTO) \
            -> Dict[str, Any]:
        """
        Converts a SnortIdsMonitorThreadStatusesDTO to a dict

        :param snort_ids_monitor_thread_statuses_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["snortIDSStatuses"] = list(map(lambda x: ClusterManagerUtil.snort_ids_status_dto_to_dict(x),
                                         snort_ids_monitor_thread_statuses_dto.snortIDSStatuses))
        return d

    @staticmethod
    def ossec_ids_monitor_thread_statuses_dto_to_dict(
            ossec_ids_monitor_thread_statuses_dto: cluster_manager_pb2.OSSECIdsMonitorThreadStatusesDTO) \
            -> Dict[str, Any]:
        """
        Converts a OSSECIdsMonitorThreadStatusesDTO to a dict

        :param ossec_ids_monitor_thread_statuses_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ossecIDSStatuses"] = list(map(lambda x: ClusterManagerUtil.ossec_ids_status_dto_to_dict(x),
                                         ossec_ids_monitor_thread_statuses_dto.ossecIDSStatuses))
        return d

    @staticmethod
    def ryu_manager_status_dto_to_dict(
            ryu_manager_status_dto_to_dict: cluster_manager_pb2.RyuManagerStatusDTO) -> Dict[str, Any]:
        """
        Converts a RyuManagerStatusDTO to a dict

        :param ryu_manager_status_dto_to_dict: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ryu_running"] = ryu_manager_status_dto_to_dict.ryu_running
        d["monitor_running"] = ryu_manager_status_dto_to_dict.monitor_running
        d["port"] = ryu_manager_status_dto_to_dict.port
        d["web_port"] = ryu_manager_status_dto_to_dict.web_port
        d["controller"] = ryu_manager_status_dto_to_dict.controller
        d["kafka_ip"] = ryu_manager_status_dto_to_dict.kafka_ip
        d["kafka_port"] = ryu_manager_status_dto_to_dict.kafka_port
        d["time_step_len"] = ryu_manager_status_dto_to_dict.time_step_len
        return d

    @staticmethod
    def host_manager_status_dto_to_dict(host_manager_status_dto: cluster_manager_pb2.HostManagerStatusDTO) \
            -> Dict[str, Any]:
        """
        Converts a HostManagerStatusDTO to a dict

        :param host_manager_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["monitor_running"] = host_manager_status_dto.monitor_running
        d["filebeat_running"] = host_manager_status_dto.filebeat_running
        d["packetbeat_running"] = host_manager_status_dto.packetbeat_running
        d["metricbeat_running"] = host_manager_status_dto.metricbeat_running
        d["heartbeat_running"] = host_manager_status_dto.heartbeat_running
        return d

    @staticmethod
    def kafka_status_dto_to_dict(kafka_status_dto: cluster_manager_pb2.KafkaStatusDTO) -> Dict[str, Any]:
        """
        Converts a KafkaStatusDTO to a dict

        :param kafka_status_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["running"] = kafka_status_dto.running
        d["topics"] = kafka_status_dto.topics
        return d

    @staticmethod
    def snort_managers_info_dto_to_dict(snort_managers_info_dto: cluster_manager_pb2.SnortIdsManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a SnortIdsManagersInfoDTO to a dict

        :param snort_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(snort_managers_info_dto.ips)
        d["ports"] = list(snort_managers_info_dto.ports)
        d["snortIdsManagersRunning"] = list(snort_managers_info_dto.snortIdsManagersRunning)
        d["snortIdsManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.snort_ids_status_dto_to_dict(x),
                                                 list(snort_managers_info_dto.snortIdsManagersStatuses)))
        d["emulationName"] = snort_managers_info_dto.emulationName
        d["executionId"] = snort_managers_info_dto.executionId
        return d

    @staticmethod
    def ossec_managers_info_dto_to_dict(ossec_managers_info_dto: cluster_manager_pb2.OSSECIdsManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a OSSECIdsManagersInfoDTO to a dict

        :param ossec_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(ossec_managers_info_dto.ips)
        d["ports"] = list(ossec_managers_info_dto.ports)
        d["ossecIdsManagersRunning"] = list(ossec_managers_info_dto.ossecIdsManagersRunning)
        d["ossecIdsManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.ossec_ids_status_dto_to_dict(x),
                                                 list(ossec_managers_info_dto.ossecIdsManagersStatuses)))
        d["emulationName"] = ossec_managers_info_dto.emulationName
        d["executionId"] = ossec_managers_info_dto.executionId
        return d

    @staticmethod
    def kafka_managers_info_dto_to_dict(kafka_managers_info_dto: cluster_manager_pb2.KafkaManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a KafkaManagersInfoDTO to a dict

        :param kafka_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(kafka_managers_info_dto.ips)
        d["ports"] = list(kafka_managers_info_dto.ports)
        d["kafkaManagersRunning"] = list(kafka_managers_info_dto.kafkaManagersRunning)
        d["kafkaManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.kafka_status_dto_to_dict(x),
                                              list(kafka_managers_info_dto.kafkaManagersStatuses)))
        d["emulationName"] = kafka_managers_info_dto.emulationName
        d["executionId"] = kafka_managers_info_dto.executionId
        return d

    @staticmethod
    def host_managers_info_dto_to_dict(host_managers_info_dto: cluster_manager_pb2.HostManagersInfoDTO) \
            -> Dict[str, Any]:
        """
        Converts a HostManagersInfoDTO to a dict

        :param host_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(host_managers_info_dto.ips)
        d["ports"] = list(host_managers_info_dto.ports)
        d["hostManagersRunning"] = list(host_managers_info_dto.hostManagersRunning)
        d["hostManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.host_manager_status_dto_to_dict(x),
                                             list(host_managers_info_dto.hostManagersStatuses)))
        d["emulationName"] = host_managers_info_dto.emulationName
        d["executionId"] = host_managers_info_dto.executionId
        return d

    @staticmethod
    def ryu_managers_info_dto_to_dict(ryu_managers_info_dto: cluster_manager_pb2.RyuManagersInfoDTO) -> Dict[str, Any]:
        """
        Converts a RyuManagersInfoDTO to a dict

        :param ryu_managers_info_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ips"] = list(ryu_managers_info_dto.ips)
        d["ports"] = list(ryu_managers_info_dto.ports)
        d["ryuManagersRunning"] = list(ryu_managers_info_dto.ryuManagersRunning)
        d["ryuManagersStatuses"] = list(map(lambda x: ClusterManagerUtil.ryu_manager_status_dto_to_dict(x),
                                            list(ryu_managers_info_dto.ryuManagersStatuses)))
        d["emulationName"] = ryu_managers_info_dto.emulationName
        d["executionId"] = ryu_managers_info_dto.executionId
        return d

    @staticmethod
    def convert_host_status_to_host_manager_status_dto(
            host_status_dto_and_ip: Tuple[csle_collector.host_manager.host_manager_pb2.HostStatusDTO, str]) -> \
            cluster_manager_pb2.HostManagerStatusDTO:
        """
        Converts a HostStatusDTO to a HostManagerStatusDTO

        :param host_status_dto: the DTO to convert
        :return: the converted DTO
        """
        host_status_dto = host_status_dto_and_ip[0]
        ip = host_status_dto_and_ip[1]
        if host_status_dto is None:
            return ClusterManagerUtil.get_empty_host_manager_status_dto()
        return cluster_manager_pb2.HostManagerStatusDTO(
            monitor_running=host_status_dto.monitor_running,
            filebeat_running=host_status_dto.filebeat_running,
            packetbeat_running=host_status_dto.packetbeat_running,
            metricbeat_running=host_status_dto.metricbeat_running,
            heartbeat_running=host_status_dto.heartbeat_running,
            ip=ip
        )

    @staticmethod
    def convert_snort_info_dto(snort_ids_managers_info_dto: SnortIdsManagersInfo) -> \
            cluster_manager_pb2.SnortIdsManagersInfoDTO:
        """
        Converts a SnortIdsManagersInfo into a SnortIdsManagersInfoDTO

        :param snort_ids_managers_info_dto: the DTO to convert
        :return: the converted DTO
        """
        if snort_ids_managers_info_dto is None:
            return ClusterManagerUtil.get_empty_snort_managers_info_dto()
        return cluster_manager_pb2.SnortIdsManagersInfoDTO(
            ips=snort_ids_managers_info_dto.ips,
            ports=snort_ids_managers_info_dto.ports,
            emulationName=snort_ids_managers_info_dto.emulation_name,
            executionId=snort_ids_managers_info_dto.execution_id,
            snortIdsManagersRunning=snort_ids_managers_info_dto.snort_ids_managers_running,
            snortIdsManagersStatuses=list(
                map(lambda x: ClusterManagerUtil.convert_snort_ids_monitor_dto_to_snort_ids_status_dto(x),
                    snort_ids_managers_info_dto.snort_ids_managers_statuses))
        )

    @staticmethod
    def convert_ossec_info_dto(ossec_ids_managers_info_dto: OSSECIDSManagersInfo) \
            -> cluster_manager_pb2.OSSECIdsManagersInfoDTO:
        """
        Converts a OSSECIDSManagersInfo into a OSSECIdsManagersInfoDTO

        :param ossec_ids_managers_info_dto: the DTO to convert
        :return: the converted DTO
        """
        if ossec_ids_managers_info_dto is None:
            return ClusterManagerUtil.get_empty_ossec_managers_info_dto()
        return cluster_manager_pb2.OSSECIdsManagersInfoDTO(
            ips=ossec_ids_managers_info_dto.ips,
            ports=ossec_ids_managers_info_dto.ports,
            emulationName=ossec_ids_managers_info_dto.emulation_name,
            executionId=ossec_ids_managers_info_dto.execution_id,
            ossecIdsManagersRunning=ossec_ids_managers_info_dto.ossec_ids_managers_running,
            ossecIdsManagersStatuses=list(map(
                lambda x: ClusterManagerUtil.convert_ossec_ids_monitor_dto_to_ossec_ids_status_dto(x),
                ossec_ids_managers_info_dto.ossec_ids_managers_statuses))
        )

    @staticmethod
    def convert_elk_info_dto(elk_managers_dto: ELKManagersInfo) -> cluster_manager_pb2.ElkManagersInfoDTO:
        """
        Converts a ELKManagersInfo into a ElkManagersInfoDTO

        :param elk_managers_dto: the DTO to convert
        :return: the converted DTO
        """
        if elk_managers_dto is None:
            return ClusterManagerUtil.get_empty_elk_managers_info_dto()
        return cluster_manager_pb2.ElkManagersInfoDTO(
            ips=elk_managers_dto.ips,
            ports=elk_managers_dto.ports,
            emulationName=elk_managers_dto.emulation_name,
            executionId=elk_managers_dto.execution_id,
            elkManagersRunning=elk_managers_dto.elk_managers_running,
            elkManagersStatuses=list(map(
                lambda x: ClusterManagerUtil.convert_elk_dto(x), elk_managers_dto.elk_managers_statuses)),
            localKibanaPort=elk_managers_dto.local_kibana_port
        )

    @staticmethod
    def convert_ryu_info_dto(ryu_managers_info_dto: RyuManagersInfo) -> cluster_manager_pb2.RyuManagersInfoDTO:
        """
        Converts a RyuManagersInfo into a RyuManagersInfoDTO

        :param ryu_managers_info_dto: the DTO to convert
        :return: the converted DTO
        """
        if ryu_managers_info_dto is None:
            return ClusterManagerUtil.get_empty_ryu_managers_info_dto()
        return cluster_manager_pb2.OSSECIdsManagersInfoDTO(
            ips=ryu_managers_info_dto.ips,
            ports=ryu_managers_info_dto.ports,
            emulationName=ryu_managers_info_dto.emulation_name,
            executionId=ryu_managers_info_dto.execution_id,
            ryuManagersRunning=ryu_managers_info_dto.ryu_managers_running,
            ryuManagersStatuses=list(
                map(lambda x: ClusterManagerUtil.convert_ossec_ids_monitor_dto_to_ossec_ids_status_dto(x),
                    ryu_managers_info_dto.ryu_managers_statuses))
        )

    @staticmethod
    def convert_host_info_dto(host_managers_dto: HostManagersInfo) -> cluster_manager_pb2.HostManagersInfoDTO:
        """
        Converts a HostManagersInfo into a HostManagersInfoDTO

        :param host_managers_dto: the DTO to convert
        :return: the converted DTO
        """
        if host_managers_dto is None:
            return ClusterManagerUtil.get_empty_host_managers_info_dto()
        return cluster_manager_pb2.HostManagersInfoDTO(
            ips=host_managers_dto.ips,
            ports=host_managers_dto.ports,
            emulationName=host_managers_dto.emulation_name,
            executionId=host_managers_dto.execution_id,
            hostManagersRunning=host_managers_dto.host_managers_running,
            hostManagersStatuses=list(
                map(lambda x: ClusterManagerUtil.convert_host_status_to_host_manager_status_dto(x),
                    host_managers_dto.host_managers_statuses))
        )

    @staticmethod
    def convert_kafka_info_dto(kafka_managers_info_dto: KafkaManagersInfo) \
            -> cluster_manager_pb2.KafkaManagersInfoDTO:
        """
        Converts a KafkaManagersInfo into a KafkaManagersInfoDTO

        :param kafka_managers_info_dto: the DTO to convert
        :return: the converted DTO
        """
        if kafka_managers_info_dto is None:
            return ClusterManagerUtil.get_empty_kafka_managers_info_dto()
        return cluster_manager_pb2.KafkaManagersInfoDTO(
            ips=kafka_managers_info_dto.ips,
            ports=kafka_managers_info_dto.ports,
            emulationName=kafka_managers_info_dto.emulation_name,
            executionId=kafka_managers_info_dto.execution_id,
            kafkaManagersRunning=kafka_managers_info_dto.kafka_managers_running,
            kafkaManagersStatuses=list(map(lambda x: ClusterManagerUtil.convert_kafka_dto_to_kafka_status_dto(x),
                                           kafka_managers_info_dto.kafka_managers_statuses))
        )

    @staticmethod
    def convert_client_info_dto(client_managers_dto: ClientManagersInfo) \
            -> cluster_manager_pb2.ClientManagersInfoDTO:
        """
        Converts a ClientManagersInfo into a ClientManagersInfoDTO

        :param client_managers_dto: the DTO to convert
        :return: the converted DTO
        """
        if client_managers_dto is None:
            return ClusterManagerUtil.get_empty_client_managers_info_dto()
        return cluster_manager_pb2.ClientManagersInfoDTO(
            ips=client_managers_dto.ips,
            ports=client_managers_dto.ports,
            emulationName=client_managers_dto.emulation_name,
            executionId=client_managers_dto.execution_id,
            clientManagersRunning=client_managers_dto.client_managers_running,
            clientManagersStatuses=list(map(lambda x: ClusterManagerUtil.convert_client_dto_to_get_num_clients_dto(x),
                                            client_managers_dto.client_managers_statuses))
        )

    @staticmethod
    def convert_traffic_info_dto(traffic_managers_dto: TrafficManagersInfo) \
            -> cluster_manager_pb2.TrafficManagerInfoDTO:
        """
        Converts a TrafficManagersInfo into a TrafficManagerInfoDTO

        :param traffic_managers_dto: the DTO to convert
        :return: the converted DTO
        """
        if traffic_managers_dto is None:
            return ClusterManagerUtil.get_empty_traffic_managers_info_dto()
        return cluster_manager_pb2.TrafficManagersInfoDTO(
            ips=traffic_managers_dto.ips,
            ports=traffic_managers_dto.ports,
            emulationName=traffic_managers_dto.emulation_name,
            executionId=traffic_managers_dto.execution_id,
            trafficManagersRunning=traffic_managers_dto.traffic_managers_running,
            trafficManagersStatuses=list(map(
                lambda x: ClusterManagerUtil.convert_traffic_dto_to_traffic_manager_info_dto(x),
                traffic_managers_dto.traffic_managers_statuses))
        )

    @staticmethod
    def convert_docker_info_dto(docker_stats_managers_dto: DockerStatsManagersInfo) \
            -> cluster_manager_pb2.DockerStatsManagersInfoDTO:
        """
        Converts a DockerStatsManagersInfo into a DockerStatsManagersInfoDTO

        :param docker_stats_managers_dto: the DTO to convert
        :return: the converted DTO
        """
        if docker_stats_managers_dto is None:
            return ClusterManagerUtil.get_empty_docker_managers_info_dto()
        return cluster_manager_pb2.DockerStatsManagersInfoDTO(
            ips=docker_stats_managers_dto.ips,
            ports=docker_stats_managers_dto.ports,
            emulationName=docker_stats_managers_dto.emulation_name,
            executionId=docker_stats_managers_dto.execution_id,
            dockerStatsManagersRunning=docker_stats_managers_dto.docker_stats_managers_running,
            dockerStatsManagersStatuses=list(map(lambda x: ClusterManagerUtil.convert_docker_stats_monitor_dto(x),
                                                 docker_stats_managers_dto.docker_stats_managers_statuses))
        )

    @staticmethod
    def convert_execution_info_dto(execution_info_dto: EmulationExecutionInfo) -> cluster_manager_pb2.ExecutionInfoDTO:
        """
        Converts a EmulationExecutionInfo into a ExecutionInfoDTO

        :param execution_info_dto: the DTO to convert
        :return: the converted DTO
        """
        if execution_info_dto is None:
            return ClusterManagerUtil.get_empty_execution_info_dto()
        running_containers = []
        for container in execution_info_dto.running_containers:
            running_containers.append(
                cluster_manager_pb2.DockerContainerDTO(
                    name=container.name, image=container.full_name_str, ip=container.get_ips()[0]
                )
            )
        stopped_containers = []
        for container in execution_info_dto.stopped_containers:
            stopped_containers.append(
                cluster_manager_pb2.DockerContainerDTO(
                    name=container.name, image=container.full_name_str, ip=container.get_ips()[0]
                )
            )
        network_names = []
        network_ids = []
        for net in execution_info_dto.active_networks:
            network_names.append(net.name)
            network_ids.append(-1)
        stopped_containers = cluster_manager_pb2.StoppedContainersDTO(
            stoppedContainers=stopped_containers
        )
        running_containers = cluster_manager_pb2.RunningContainersDTO(
            runningContainers=running_containers
        )
        activeNetworks = cluster_manager_pb2.DockerNetworksDTO(
            networks=network_names, network_ids=network_ids
        )
        return cluster_manager_pb2.ExecutionInfoDTO(
            emulationName=execution_info_dto.emulation_name,
            executionId=execution_info_dto.execution_id,
            snortIdsManagersInfo=ClusterManagerUtil.convert_snort_info_dto(execution_info_dto.snort_ids_managers_info),
            ossecIdsManagersInfo=ClusterManagerUtil.convert_ossec_info_dto(execution_info_dto.ossec_ids_managers_info),
            kafkaManagersInfo=ClusterManagerUtil.convert_kafka_info_dto(execution_info_dto.kafka_managers_info),
            hostManagersInfo=ClusterManagerUtil.convert_host_info_dto(execution_info_dto.host_managers_info),
            clientManagersInfo=ClusterManagerUtil.convert_client_info_dto(execution_info_dto.client_managers_info),
            dockerStatsManagersInfo=ClusterManagerUtil.convert_docker_info_dto(
                execution_info_dto.docker_stats_managers_info),
            runningContainers=running_containers, stoppedContainers=stopped_containers,
            trafficManagersInfoDTO=ClusterManagerUtil.convert_traffic_info_dto(
                execution_info_dto.traffic_managers_info),
            activeNetworks=activeNetworks,
            elkManagersInfoDTO=ClusterManagerUtil.convert_elk_info_dto(execution_info_dto.elk_managers_info),
            ryuManagersInfoDTO=ClusterManagerUtil.convert_ryu_info_dto(execution_info_dto.ryu_managers_info),
        )

    @staticmethod
    def get_empty_kafka_dto() -> cluster_manager_pb2.KafkaStatusDTO:
        """
        :return: an empty KafkaStatusDTO
        """
        return cluster_manager_pb2.KafkaStatusDTO(
            running=False, topics=[]
        )

    @staticmethod
    def get_empty_ryu_manager_status_dto() -> cluster_manager_pb2.RyuManagerStatusDTO:
        """
        :return: an empty RyuManagerStatusDTO
        """
        return cluster_manager_pb2.RyuManagerStatusDTO(
            ryu_running=False, monitor_running=False, port=-1, web_port=-1, controller="", kafka_ip="",
            kafka_port=-1, time_step_len=-1
        )

    @staticmethod
    def get_empty_docker_stats_monitor_status_dto() -> cluster_manager_pb2.DockerStatsMonitorStatusDTO:
        """
        :return: an empty DockerStatsMonitorStatusDTO
        """
        return cluster_manager_pb2.DockerStatsMonitorStatusDTO(num_monitors=0, emulations=[], emulation_executions=[])

    @staticmethod
    def get_empty_num_clients_dto() -> cluster_manager_pb2.GetNumClientsDTO:
        """
        :return: an empty GetNumClientsDTO
        """
        return cluster_manager_pb2.GetNumClientsDTO(
            num_clients=0, client_process_active=False, producer_active=False, clients_time_step_len_seconds=-1,
            producer_time_step_len_seconds=-1)

    @staticmethod
    def get_empty_elk_status_dto() -> cluster_manager_pb2.ElkStatusDTO:
        """
        :return: an empty ElkStatusDTO
        """
        return cluster_manager_pb2.ElkStatusDTO(elasticRunning=False, kibanaRunning=False, logstashRunning=False)

    @staticmethod
    def get_empty_snort_ids_status_dto() -> cluster_manager_pb2.SnortIdsStatusDTO:
        """
        :return: an empty SnortIdsStatusDTO
        """
        return cluster_manager_pb2.SnortIdsStatusDTO(monitor_running=False, snort_ids_running=False)

    @staticmethod
    def get_empty_ossec_ids_monitor_dto() -> cluster_manager_pb2.OSSECIdsStatusDTO:
        """
        :return: an empty OSSECIdsMonitorDTO
        """
        return cluster_manager_pb2.OSSECIdsStatusDTO(monitor_running=False, ossec_ids_running=False)

    @staticmethod
    def get_empty_host_manager_status_dto() -> cluster_manager_pb2.HostManagerStatusDTO:
        """
        :return: an empty HostManagerStatusDTO
        """
        return cluster_manager_pb2.HostManagerStatusDTO(
            monitor_running=False, filebeat_running=False, packetbeat_running=False, metricbeat_running=False,
            heartbeat_running=False, ip="")

    @staticmethod
    def get_empty_snort_managers_info_dto() -> cluster_manager_pb2.SnortIdsManagersInfoDTO:
        """
        :return: an empty SnortIdsManagersInfoDTO
        """
        return cluster_manager_pb2.SnortIdsManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", snortIdsManagersRunning=[], snortIdsManagersStatuses=[]
        )

    @staticmethod
    def get_empty_ossec_managers_info_dto() -> cluster_manager_pb2.OSSECIdsManagersInfoDTO:
        """
        :return: an empty OSSECIdsManagersInfoDTO
        """
        return cluster_manager_pb2.OSSECIdsManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", ossecIdsManagersRunning=[], ossecIdsManagersStatuses=[]
        )

    @staticmethod
    def get_empty_elk_managers_info_dto() -> cluster_manager_pb2.ElkManagersInfoDTO:
        """
        :return: an empty ElkManagersInfoDTO
        """
        return cluster_manager_pb2.ElkManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", elkManagersRunning=[], elkManagersStatuses=[],
            localKibanaPort=-1
        )

    @staticmethod
    def get_empty_ryu_managers_info_dto() -> cluster_manager_pb2.RyuManagersInfoDTO:
        """
        :return: an empty RyuManagersInfoDTO
        """
        return cluster_manager_pb2.RyuManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId=-1, ryuManagersRunning=[], ryuManagersStatuses=[]
        )

    @staticmethod
    def get_empty_host_managers_info_dto() -> cluster_manager_pb2.HostManagersInfoDTO:
        """
        :return: an empty HostManagersInfoDTO
        """
        return cluster_manager_pb2.HostManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", hostManagersRunning=[], hostManagersStatuses=[]
        )

    @staticmethod
    def get_empty_kafka_managers_info_dto() -> cluster_manager_pb2.KafkaManagersInfoDTO:
        """
        :return: an empty KafkaManagersInfoDTO
        """
        return cluster_manager_pb2.KafkaManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", hostManagersRunning=[], hostManagersStatuses=[]
        )

    @staticmethod
    def get_empty_docker_managers_info_dto() -> cluster_manager_pb2.DockerStatsManagersInfoDTO:
        """
        :return: an empty DockerStatsManagersInfoDTO
        """
        return cluster_manager_pb2.DockerStatsManagersInfoDTO(
            ips=[], ports=[], emulationName="", executionId="", dockerStatsManagersRunning=[],
            dockerStatsManagersStatuses=[]
        )

    @staticmethod
    def get_empty_execution_info_dto() -> cluster_manager_pb2.ExecutionInfoDTO:
        """
        :return: an empty ExecutionInfoDTO
        """
        return cluster_manager_pb2.ExecutionInfoDTO(
            emulationName="", executionId="", snortIdsManagersInfo=None, ossecIdsManagersInfo=None,
            kafkaManagersInfo=None, hostManagersInfo=None, clientManagersInfo=None, dockerStatsManagersInfo=None,
            runningContainers=[], elkManagersInfoDTO=None, ryuManagersInfoDTO=None, trafficManagersInfoDTO=None,
            stoppedContainers=[], activeNetworks=[]
        )

    @staticmethod
    def get_empty_kibana_tunnel_dto() -> cluster_manager_pb2.KibanaTunnelDTO:
        """
        :return: an empty KibanaTunnelDTO
        """
        return cluster_manager_pb2.KibanaTunnelDTO(port=1, ip="", emulation="", ipFirstOctet=-1)

    @staticmethod
    def get_empty_kibana_tunnels_dto() -> cluster_manager_pb2.KibanaTunnelsDTO:
        """
        :return: an empty KibanaTunnelsDTO
        """
        return cluster_manager_pb2.KibanaTunnelsDTO(tunnels=[])

    @staticmethod
    def kibana_tunnel_dto_to_dict(kibana_tunnel_dto: cluster_manager_pb2.KibanaTunnelDTO) -> Dict[str, Any]:
        """
        Converts a KibanaTunnelDTO to a dict

        :param kibana_tunnel_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ip"] = kibana_tunnel_dto.ip
        d["port"] = kibana_tunnel_dto.port
        d["emulation"] = kibana_tunnel_dto.emulation
        d["ipFirstOctet"] = kibana_tunnel_dto.ipFirstOctet
        return d

    @staticmethod
    def kibana_tunnels_dto_to_dict(kibana_tunnels_dto: cluster_manager_pb2.KibanaTunnelsDTO) -> Dict[str, Any]:
        """
        Converts a KibanaTunnelsDTO to a dict

        :param kibana_tunnels_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["tunnels"] = list(map(lambda x: ClusterManagerUtil.kibana_tunnel_dto_to_dict(kibana_tunnel_dto=x),
                                kibana_tunnels_dto.tunnels))
        return d

    @staticmethod
    def get_empty_ryu_tunnel_dto() -> cluster_manager_pb2.RyuTunnelDTO:
        """
        :return: an empty RyuTunnelDTO
        """
        return cluster_manager_pb2.RyuTunnelDTO(port=1, ip="", emulation="", ipFirstOctet=-1)

    @staticmethod
    def get_empty_ryu_tunnels_dto() -> cluster_manager_pb2.RyuTunnelsDTO:
        """
        :return: an empty RyuTunnelsDTO
        """
        return cluster_manager_pb2.RyuTunnelsDTO(tunnels=[])

    @staticmethod
    def ryu_tunnel_dto_to_dict(ryu_tunnel_dto: cluster_manager_pb2.RyuTunnelDTO) -> Dict[str, Any]:
        """
        Converts a RyuTunnelDTO to a dict

        :param ryu_tunnel_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["ip"] = ryu_tunnel_dto.ip
        d["port"] = ryu_tunnel_dto.port
        d["emulation"] = ryu_tunnel_dto.emulation
        d["ipFirstOctet"] = ryu_tunnel_dto.ipFirstOctet
        return d

    @staticmethod
    def ryu_tunnels_dto_to_dict(ryu_tunnels_dto: cluster_manager_pb2.RyuTunnelsDTO) -> Dict[str, Any]:
        """
        Converts a RyuTunnelsDTO to a dict

        :param ryu_tunnels_dto: the dto to convert
        :return: a dict representation of the DTO
        """
        d = {}
        d["tunnels"] = list(map(lambda x: ClusterManagerUtil.ryu_tunnel_dto_to_dict(ryu_tunnel_dto=x),
                                ryu_tunnels_dto.tunnels))
        return d

    @staticmethod
    def create_kibana_tunnel(execution: EmulationExecution, logger: logging.Logger) -> int:
        """
        Utility method for creating a Kibana tunnel.

        :param execution: the execution to create the tunnel for
        :param logger: the logger to use for logging
        :return: the port of the tunnel
        """
        ip = GeneralUtil.get_host_ip()
        if ip != execution.emulation_env_config.elk_config.container.physical_host_ip:
            return -1
        try:
            local_kibana_port = cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNEL_BASE_PORT + execution.ip_first_octet
            if execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip \
                    not in cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT:
                try:
                    EmulationEnvController.create_ssh_tunnel(
                        tunnels_dict=cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT,
                        local_port=local_kibana_port,
                        remote_port=execution.emulation_env_config.elk_config.kibana_port,
                        remote_ip=execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip,
                        emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
                except Exception:
                    local_kibana_port = local_kibana_port + 100
                    EmulationEnvController.create_ssh_tunnel(
                        tunnels_dict=cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT,
                        local_port=local_kibana_port,
                        remote_port=execution.emulation_env_config.elk_config.kibana_port,
                        remote_ip=execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip,
                        emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
            else:
                tunnel_thread_dict = cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT[
                    execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip]
                try:
                    response = get(f'{constants.HTTP.HTTP_PROTOCOL_PREFIX}{constants.COMMON.LOCALHOST}:'
                                   f'{local_kibana_port}')
                    if response.status_code != constants.HTTPS.OK_STATUS_CODE:
                        tunnel_thread_dict[cluster_constants.KIBANA_TUNNELS.THREAD_PROPERTY].shutdown()
                        del cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT[
                            execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip]
                        EmulationEnvController.create_ssh_tunnel(
                            tunnels_dict=cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT,
                            local_port=local_kibana_port,
                            remote_port=execution.emulation_env_config.elk_config.kibana_port,
                            remote_ip=execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip,
                            emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
                except Exception:
                    tunnel_thread_dict[cluster_constants.KIBANA_TUNNELS.THREAD_PROPERTY].shutdown()
                    if execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip in \
                            cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT:
                        del cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT[
                            execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip]
                    local_kibana_port = local_kibana_port + 100
                    EmulationEnvController.create_ssh_tunnel(
                        tunnels_dict=cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT,
                        local_port=local_kibana_port, remote_port=execution.emulation_env_config.elk_config.kibana_port,
                        remote_ip=execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip,
                        emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
            return local_kibana_port
        except Exception as e:
            logger.warning(f"There was an exception creating the Kibana tunnel: {str(e)}, {repr(e)}")
            return -1

    @staticmethod
    def remove_kibana_tunnel(execution: EmulationExecution) -> None:
        """
        Utility function for removing the kibana tunnel of a given execution

        :param execution: the execution to remove the tunnel for
        :return: None
        """
        if execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip in \
                cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT:
            tunnel_thread_dict = cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT[
                execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip]
            tunnel_thread_dict[cluster_constants.KIBANA_TUNNELS.THREAD_PROPERTY].shutdown()
            del cluster_constants.KIBANA_TUNNELS.KIBANA_TUNNELS_DICT[
                execution.emulation_env_config.elk_config.container.docker_gw_bridge_ip]

    @staticmethod
    def create_ryu_tunnel(execution: EmulationExecution, logger: logging.Logger) -> int:
        """
        Utility function for creating a Ryu tunnel

        :param execution: the execution to create the tunnel for
        :param logger: the logger to use for logging
        :return: the port of the tunnel
        """
        try:
            local_ryu_port = cluster_constants.RYU_TUNNELS.RYU_TUNNEL_BASE_PORT + execution.ip_first_octet
            if execution.emulation_env_config.sdn_controller_config is not None:
                if execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip \
                        not in cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT:
                    try:
                        EmulationEnvController.create_ssh_tunnel(
                            tunnels_dict=cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT,
                            local_port=local_ryu_port,
                            remote_port=execution.emulation_env_config.sdn_controller_config.controller_web_api_port,
                            remote_ip=
                            execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip,
                            emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
                    except Exception:
                        local_ryu_port = local_ryu_port + 100
                        EmulationEnvController.create_ssh_tunnel(
                            tunnels_dict=cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT,
                            local_port=local_ryu_port,
                            remote_port=execution.emulation_env_config.sdn_controller_config.controller_web_api_port,
                            remote_ip=
                            execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip,
                            emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
                else:
                    tunnel_thread_dict = cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT[
                        execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip]
                    try:
                        response = get(f'{constants.HTTP.HTTP_PROTOCOL_PREFIX}{constants.COMMON.LOCALHOST}:'
                                       f'{local_ryu_port}')
                        if response.status_code != constants.HTTPS.OK_STATUS_CODE:
                            tunnel_thread_dict[cluster_constants.RYU_TUNNELS.THREAD_PROPERTY].shutdown()
                            del cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT[
                                execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip]
                            EmulationEnvController.create_ssh_tunnel(
                                tunnels_dict=cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT,
                                local_port=local_ryu_port,
                                remote_port=execution.emulation_env_config.sdn_controller_config.controller_web_api_port,
                                remote_ip=
                                execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip,
                                emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
                    except Exception:
                        tunnel_thread_dict[cluster_constants.RYU_TUNNELS.THREAD_PROPERTY].shutdown()
                        if execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip in \
                                cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT:
                            del cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT[
                                execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip]
                        local_ryu_port = local_ryu_port + 100
                        EmulationEnvController.create_ssh_tunnel(
                            tunnels_dict=cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT,
                            local_port=local_ryu_port,
                            remote_port=execution.emulation_env_config.sdn_controller_config.controller_web_api_port,
                            remote_ip=
                            execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip,
                            emulation=execution.emulation_name, execution_id=execution.ip_first_octet)
            return local_ryu_port
        except Exception as e:
            logger.warning(
                f"There was an exception creating the Ryu tunnel: {str(e)}, {repr(e)}")
            return -1

    @staticmethod
    def remove_ryu_tunnel(execution: EmulationExecution) -> None:
        """
        Utility function for removing a Ryu tunnel for a given execution

        :param execution: the execution to remove the tunnel for
        :return: None
        """
        if execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip \
                in cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT:
            tunnel_thread_dict = cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT[
                execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip]
            tunnel_thread_dict[cluster_constants.RYU_TUNNELS.THREAD_PROPERTY].shutdown()
            del cluster_constants.RYU_TUNNELS.RYU_TUNNELS_DICT[
                execution.emulation_env_config.sdn_controller_config.container.docker_gw_bridge_ip]

    @staticmethod
    def create_kibana_tunnels_dto_from_dict(dict: Dict[str, Any]) -> cluster_manager_pb2.KibanaTunnelsDTO:
        """
        Utility function for creating a kibana tunnels DTO from a dict with Kibana tunnels

        :param dict: the dict with the tunnels
        :return: the DTO
        """
        kibana_tunnels = []
        for k,v in dict.items():
            kibana_tunnels.append(cluster_manager_pb2.KibanaTunnelDTO(
                ip=k, port = v[constants.GENERAL.PORT_PROPERTY], emulation = v[constants.GENERAL.EMULATION_PROPERTY],
                ipFirstOctet = v[constants.GENERAL.EXECUTION_ID_PROPERTY]
            ))
        return cluster_manager_pb2.KibanaTunnelsDTO(tunnels=kibana_tunnels)

    @staticmethod
    def create_ryu_tunnels_dto_from_dict(dict: Dict[str, Any]) -> cluster_manager_pb2.RyuTunnelsDTO:
        """
        Utility function for creating a ryu tunnels DTO from a dict with Ryu tunnels

        :param dict: the dict with the tunnels
        :return: the DTO
        """
        ryu_tunnels = []
        for k,v in dict.items():
            ryu_tunnels.append(cluster_manager_pb2.RyuTunnelDTO(
                ip=k, port = v[constants.GENERAL.PORT_PROPERTY], emulation = v[constants.GENERAL.EMULATION_PROPERTY],
                ipFirstOctet = v[constants.GENERAL.EXECUTION_ID_PROPERTY]
            ))
        return cluster_manager_pb2.RyuTunnelsDTO(tunnels=ryu_tunnels)

    @staticmethod
    def merge_execution_infos(execution_infos: List[cluster_manager_pb2.ExecutionInfoDTO]) \
            -> cluster_manager_pb2.ExecutionInfoDTO:
        """
        Function that merges a list of execution infos into one

        :param execution_infos: the list of execution infos to merge
        :return: the merged info
        """
        assert len(execution_infos) > 0
        if len(execution_infos) == 1:
            return execution_infos[0]
        merged_info = execution_infos[0]
        for exec_info in execution_infos[1:]:
            merged_info.snortIdsManagersInfo = merged_info.snortIdsManagersInfo + exec_info.snortIdsManagersInfo
            merged_info.ossecIdsManagersInfo = merged_info.ossecIdsManagersInfo + exec_info.ossecIdsManagersInfo
            merged_info.kafkaManagersInfo = merged_info.kafkaManagersInfo + exec_info.kafkaManagersInfo
            merged_info.hostManagersInfo = merged_info.hostManagersInfo + exec_info.hostManagersInfo
            merged_info.clientManagersInfo = merged_info.clientManagersInfo + exec_info.clientManagersInfo
            merged_info.dockerStatsManagersInfo = merged_info.dockerStatsManagersInfo + \
                                                  exec_info.dockerStatsManagersInfo
            merged_info.runningContainers = merged_info.runningContainers + exec_info.runningContainers
            merged_info.stoppedContainers = merged_info.stoppedContainers + exec_info.stoppedContainers
            merged_info.trafficManagersInfoDTO = merged_info.trafficManagersInfoDTO + exec_info.trafficManagersInfoDTO
            merged_info.activeNetworks = merged_info.activeNetworks + exec_info.activeNetworks
            merged_info.elkManagersInfoDTO = merged_info.elkManagersInfoDTO + exec_info.elkManagersInfoDTO
            merged_info.ryuManagersInfoDTO = merged_info.ryuManagersInfoDTO + exec_info.ryuManagersInfoDTO
        return merged_info