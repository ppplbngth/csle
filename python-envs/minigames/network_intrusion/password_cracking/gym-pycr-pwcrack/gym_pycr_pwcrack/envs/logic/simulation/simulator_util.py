from typing import List, Union
import numpy as np
from gym_pycr_pwcrack.dao.network.env_state import EnvState
from gym_pycr_pwcrack.dao.network.env_config import EnvConfig
from gym_pycr_pwcrack.dao.action.action import Action
from gym_pycr_pwcrack.dao.network.transport_protocol import TransportProtocol
from gym_pycr_pwcrack.dao.observation.machine_observation_state import MachineObservationState
from gym_pycr_pwcrack.dao.observation.port_observation_state import PortObservationState
from gym_pycr_pwcrack.dao.observation.vulnerability_observation_state import VulnerabilityObservationState

class SimulatorUtil:
    """
    Class containing utility functions for the simulator
    """

    @staticmethod
    def merge_new_obs_with_old(old_machines_obs: List[MachineObservationState],
                               new_machines_obs: List[MachineObservationState]) -> \
            Union[List[MachineObservationState], int, int, int, int]:
        """
        Helper function for merging an old network observation with new information collected

        :param old_machines_obs: the list of old machine observations
        :param new_machines_obs: the list of newly collected information
        :return: the merged machine information, n_new_ports, n_new_os, n_new_vuln, n_new_m
        """
        merged_machines = []
        total_new_ports_found, total_new_os_found, total_new_vuln_found, total_new_machines = 0,0,0,0

        # Add updated machines to merged state
        for n_m in new_machines_obs:
            exists = False
            merged_m = n_m
            for i, o_m in enumerate(old_machines_obs):
                if n_m.ip == o_m.ip:
                    merged_m, num_new_ports_found, num_new_os_found, num_new_vuln_found = \
                        SimulatorUtil.merge_new_machine_obs_with_old_machine_obs(o_m, n_m)
                    total_new_ports_found += num_new_ports_found
                    total_new_os_found += num_new_os_found
                    total_new_vuln_found += num_new_vuln_found
                    exists = True
            merged_machines.append(merged_m)
            if not exists:
                total_new_ports_found += len(merged_m.ports)
                new_os = 0 if merged_m.os == "unknown" else 1
                total_new_os_found += new_os
                total_new_vuln_found += len(merged_m.vuln)
                total_new_machines += 1

        # Add old machines to merged state
        for o_m in old_machines_obs:
            exists = False
            for m_m in merged_machines:
                if o_m.ip == m_m.ip:
                    exists = True
            if not exists:
                merged_machines.append(o_m)

        return merged_machines, total_new_ports_found, total_new_os_found, total_new_vuln_found, total_new_machines

    @staticmethod
    def merge_new_machine_obs_with_old_machine_obs(o_m: MachineObservationState, n_m: MachineObservationState) \
            -> Union[MachineObservationState, int, int, int]:
        """
        Helper function for merging an old machine observation with new information collected
        :param o_m: old machine observation
        :param n_m: newly collected machine information
        :return: the merged machine observation state, n_new_ports, n_new_os, n_new_vuln
        """
        if n_m == None:
            return o_m
        merged_ports, num_new_ports_found = SimulatorUtil.merge_ports(o_m.ports, n_m.ports)
        n_m.ports = merged_ports
        merged_os, num_new_os_found = SimulatorUtil.merge_os(o_m.os, n_m.os)
        n_m.os = merged_os
        merged_vulnerabilities, num_new_vuln_found = SimulatorUtil.merge_vulnerabilities(o_m.vuln, n_m.vuln)
        n_m.vuln = merged_vulnerabilities
        return n_m, num_new_ports_found, num_new_os_found, num_new_vuln_found

    @staticmethod
    def merge_os(o_os : str, n_os : str) -> Union[str, int]:
        """
        Helper function for merging an old machine observation OS with new information collected

        :param o_os: the old OS
        :param n_os: the newly observed OS
        :return: the merged os, 1 if it was a newly detected OS, otherwise 0
        """
        merged_os = n_os
        if n_os == "unknown" and o_os != "unknown":
            merged_os = o_os
        new_os = 0 if merged_os == o_os else 1
        return merged_os, new_os

    @staticmethod
    def merge_ports(o_ports: List[PortObservationState], n_ports: List[PortObservationState], acc : bool = True) \
            -> Union[List[PortObservationState], int]:
        """
        Helper function for merging two port lists

        :param o_ports: old list of ports
        :param n_ports: new list of ports
        :param acc: if true, accumulate port observations rather than overwrite
        :return: the merged port list, number of new ports found
        """
        num_new_ports_found = 0
        if n_ports == None or len(n_ports) == 0:
            return o_ports, num_new_ports_found
        merged_ports = n_ports
        for m_p in merged_ports:
            exist = False
            for o_p in o_ports:
                if o_p.port == m_p.port and o_p.protocol == m_p.protocol and o_p.service == m_p.service \
                        and o_p.open == m_p.open:
                    exist = True
            if not exist:
                num_new_ports_found += 1
        if acc:
            for o_p in o_ports:
                exist = False
                for m_p in merged_ports:
                    if o_p.port == m_p.port and o_p.protocol == m_p.protocol:
                        exist = True
                if not exist:
                    merged_ports.append(o_p)
        return merged_ports, num_new_ports_found

    @staticmethod
    def merge_vulnerabilities(o_vuln: List[VulnerabilityObservationState], n_vuln: List[VulnerabilityObservationState],
                              acc: bool = True) -> Union[List[VulnerabilityObservationState], int]:
        """
        Helper function for merging two vulnerability lists lists

        :param o_vuln: old list of vulnerabilities
        :param n_vuln: new list of vulnerabilities
        :param acc: if true, accumulate vulnerability observations rather than overwrite
        :return: the merged vulnerability list, number of new vulnerabilities detected
        """
        num_new_vuln_found = 0
        if n_vuln == None or len(n_vuln) == 0:
            return o_vuln, num_new_vuln_found
        merged_vuln = n_vuln
        for m_v in merged_vuln:
            exist = False
            for o_v in o_vuln:
                if o_v.name == m_v.name:
                    exist = True
            if not exist:
                num_new_vuln_found += 1
        if acc:
            for o_v in o_vuln:
                exist = False
                for m_v in merged_vuln:
                    if o_v.name == m_v.name:
                        exist = True
                if not exist:
                    merged_vuln.append(o_v)
        return merged_vuln, num_new_vuln_found

    @staticmethod
    def simulate_port_vuln_scan_helper(s: EnvState, a: Action, env_config: EnvConfig, miss_p: float,
                                       protocol=TransportProtocol.TCP, vuln_scan : bool = False) -> Union[EnvState, int]:
        """
        Helper function for simulating port-scan and vuln-scan actions

        :param s: the current environment state
        :param a: the scan action to take
        :param env_config: the current environment configuration
        :param miss_p: the simulated probability that the scan action will not detect a real service or node
        :param protocol: the tranport protocol for the scan
        :param vuln_scan: boolean flag whether the scan is a vulnerability scan or not
        :return: s_prime, reward
        """
        total_new_ports, total_new_os, total_new_vuln, total_new_machines = 0, 0, 0, 0

        # Scan action on a single host
        if not a.subnet:
            new_m_obs = None
            for node in env_config.network_conf.nodes:
                if node.ip == a.ip:
                    new_m_obs = MachineObservationState(ip=node.ip)
                    for service in node.services:
                        if service.protocol == protocol and \
                                not np.random.rand() < miss_p:
                            port_obs = PortObservationState(port=service.port, open=True, service=service.name,
                                                            protocol=protocol)
                            new_m_obs.ports.append(port_obs)

                    if vuln_scan:
                        for vuln in node.vulnerabilities:
                            if not np.random.rand() < miss_p:
                                vuln_obs = VulnerabilityObservationState(name=vuln.name, port=vuln.port,
                                                                         protocol=vuln.protocol, cvss=vuln.cvss)
                                new_m_obs.vuln.append(vuln_obs)

            new_machines_obs = []
            merged = False
            for o_m in s.obs_state.machines:
                # Machine was already known, merge state
                if o_m.ip == a.ip:
                    merged_machine_obs, num_new_ports_found, num_new_os_found, num_new_vuln_found = \
                        SimulatorUtil.merge_new_machine_obs_with_old_machine_obs(s.obs_state.machines, new_m_obs)
                    new_machines_obs.append(merged_machine_obs)
                    merged = True
                    total_new_ports += num_new_ports_found
                    total_new_os += num_new_os_found
                    total_new_vuln += num_new_vuln_found
                else:
                    new_machines_obs.append(o_m)
            # New machine, was not known before
            if not merged:
                new_machines_obs.append(new_m_obs)
                total_new_machines +=1
            s_prime = s
            s_prime.obs_state.machines = new_machines_obs
            reward = SimulatorUtil.reward_function(num_new_ports_found=total_new_ports, num_new_os_found=total_new_os,
                                                   num_new_vuln_found=total_new_vuln, num_successful_exploit=0,
                                                   total_new_machines=total_new_machines)

        # Scan action on a whole subnet
        else:
            new_m_obs = []
            for node in env_config.network_conf.nodes:
                m_obs = MachineObservationState(ip=node.ip)
                for service in node.services:
                    if service.protocol == protocol and \
                            not np.random.rand() < miss_p:
                        port_obs = PortObservationState(port=service.port, open=True, service=service.name,
                                                        protocol=protocol)
                        m_obs.ports.append(port_obs)

                if vuln_scan:
                    for vuln in node.vulnerabilities:
                        if not np.random.rand() < miss_p:
                            vuln_obs = VulnerabilityObservationState(name=vuln.name, port=vuln.port,
                                                                     protocol=vuln.protocol, cvss=vuln.cvss)
                            m_obs.vuln.append(vuln_obs)

                new_m_obs.append(m_obs)
            new_machines_obs, total_new_ports, total_new_os, total_new_vuln, total_new_machines = \
                SimulatorUtil.merge_new_obs_with_old(s.obs_state.machines, new_m_obs)
            s_prime = s
            s_prime.obs_state.machines = new_machines_obs
            reward = SimulatorUtil.reward_function(num_new_ports_found=total_new_ports, num_new_os_found=total_new_os,
                                                   num_new_vuln_found=total_new_vuln, num_successful_exploit=0,
                                                   num_new_machines = total_new_machines)
        return s_prime, reward

    @staticmethod
    def simulate_host_scan_helper(s: EnvState, a: Action, env_config: EnvConfig, miss_p: float, os=False) -> \
            Union[EnvState, int]:
        """
        Helper method for simulating a host-scan (i.e non-port scan) action

        :param s: the current environment state
        :param a: the action to take
        :param env_config: the current environment configuration
        :param miss_p: the simulated probability that the scan action will not detect a real service or node
        :param os: boolean flag whether the host scan should check the operating system too
        :return: s_prime, reward
        """
        total_new_ports, total_new_os, total_new_vuln, total_new_machines = 0,0,0,0
        # Scan a whole subnetwork
        if not a.subnet:
            new_m_obs = None
            for node in env_config.network_conf.nodes:
                if node.ip == a.ip and not np.random.rand() < miss_p:
                    new_m_obs = MachineObservationState(ip=node.ip)
                    if os:
                        new_m_obs.os = node.os
            new_machines_obs = []
            merged = False
            for o_m in s.obs_state.machines:

                # Existing machine, it was already known
                if o_m.ip == a.ip:
                    merged_machine_obs, num_new_ports_found, num_new_os_found, num_new_vuln_found = \
                        SimulatorUtil.merge_new_machine_obs_with_old_machine_obs(s.obs_state.machines, new_m_obs)
                    new_machines_obs.append(merged_machine_obs)
                    merged = True
                    total_new_ports += num_new_ports_found
                    total_new_os += num_new_os_found
                    total_new_vuln += num_new_vuln_found
                else:
                    new_machines_obs.append(o_m)

            # New machine, it was not known before
            if not merged:
                total_new_machines += 1
                new_machines_obs.append(new_m_obs)
            s_prime = s
            s_prime.obs_state.machines = new_machines_obs
            reward = SimulatorUtil.reward_function(num_new_ports_found=total_new_ports, num_new_os_found=total_new_os,
                                                   num_new_vuln_found=total_new_vuln, num_successful_exploit=0,
                                                   num_new_machines=total_new_machines)

        # Scan a single host
        else:
            new_m_obs = []
            for node in env_config.network_conf.nodes:
                if not np.random.rand() < miss_p:
                    m_obs = MachineObservationState(ip=node.ip)
                    if os:
                        m_obs.os = node.os
                    new_m_obs.append(m_obs)
            new_machines_obs, total_new_ports, total_new_os, total_new_vuln, total_new_machines = \
                SimulatorUtil.merge_new_obs_with_old(s.obs_state.machines, new_m_obs)
            s_prime = s
            s_prime.obs_state.machines = new_machines_obs

            reward = SimulatorUtil.reward_function(num_new_ports_found=total_new_ports, num_new_os_found=total_new_os,
                                                   num_new_vuln_found=total_new_vuln, num_successful_exploit=0,
                                                   num_new_machines=total_new_machines)
        return s_prime, reward

    @staticmethod
    def reward_function(num_new_ports_found : int = 0, num_new_os_found : int = 0, num_new_vuln_found: int= 0,
                        num_successful_exploit : int = 0, num_new_machines : int = 0) -> int:
        """
        Implements the reward function

        :param num_new_ports_found: number of new ports detected
        :param num_new_os_found: number of new operating systems detected
        :param num_new_vuln_found: number of new vulnerabilities detected
        :param num_successful_exploit: number of successful exploits
        :param num_new_machines: number of new machines
        :return: reward
        """
        reward = num_new_ports_found + num_new_os_found + num_new_vuln_found + num_successful_exploit + num_new_machines
        return reward