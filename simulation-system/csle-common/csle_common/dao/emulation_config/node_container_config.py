from typing import List, Tuple
from csle_common.dao.emulation_config.container_network import ContainerNetwork


class NodeContainerConfig:
    """
    A DTO object representing an individual container in an emulation environment
    """

    def __init__(self, name: str, ips_and_networks: List[Tuple[str, ContainerNetwork]],
                 version: str, level: str, restart_policy: str,
                 suffix: str, os: str):
        """
        Intializes the DTO

        :param name: the name of the node container
        :param ips_and_networks: the list of ips and networks that the container is connected to
        :param version: the version of the container
        :param level: the level of the container
        :param restart_policy: the restart policy of the container
        :param suffix: the suffix of the container id
        :param os: the operating system of the container
        """
        self.name = name
        self.ips_and_networks = ips_and_networks
        self.version = version
        self.level = level
        self.restart_policy = restart_policy
        self.suffix = suffix
        self.os = os

    def get_ips(self) -> List[str]:
        """
        :return: a list of ips that this container has
        """
        return list(filter(lambda x: x is not None, map(lambda x: x[0], self.ips_and_networks)))

    def to_dict(self) -> dict:
        """
        :return: a dict representation of the object
        """
        d = {}
        d["name"] = self.name
        d["ips_and_networks"] = list(map(lambda x: (x[0], x[1].to_dict()), self.ips_and_networks))
        d["version"] = self.version
        d["restart_policy"] = self.restart_policy
        d["suffix"] = self.suffix
        d["os"] = self.os
        return d

    def __str__(self) -> str:
        """
        :return: a string representation of the object
        """
        return f"name{self.name}, ips and networks: {self.ips_and_networks}, version: {self.version}, " \
               f"level:{self.level}, restart_policy: {self.restart_policy}, " \
               f"suffix:{self.suffix}, os:{self.os}"


    def reachable(self, reachable_ips: List[str]) -> bool:
        """
        Check if container is reachable given a list of reachable ips

        :param reachable_ips: the list of reachable ips
        :return: True if the container is reachable, false otherwise
        """
        for ip in self.get_ips():
            if ip in reachable_ips:
                return True
        return False