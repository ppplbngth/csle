import os
from pycr_common.dao.container_config.topology import Topology
from pycr_common.dao.container_config.node_firewall_config import NodeFirewallConfig
from pycr_common.util.experiments_util import util
from pycr_common.dao.network.emulation_config import EmulationConfig
from pycr_common.envs_model.config.generator.topology_generator import TopologyGenerator
import pycr_common.constants.constants as constants


def default_topology() -> Topology:
    node_1 = NodeFirewallConfig(ip="172.18.10.10", hostname="router2",
                           output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79",
                                              "172.18.10.191", "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19",
                                              "172.18.10.31",
                                              "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                              "172.18.10.11", "172.18.10.104"]),
                           input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79",
                                             "172.18.10.191", "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19",
                                             "172.18.10.31",
                                             "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                             "172.18.10.11", "172.18.10.104"]),
                           forward_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79",
                                             "172.18.10.191", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                               "172.18.10.42",
                                               "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                               "172.18.10.11", "172.18.10.104"]),
                           output_drop = set(), input_drop = set(), forward_drop = set(), routes=set(),
                           default_input = "DROP", default_output = "DROP", default_forward="DROP",
                           default_gw=None
                           )
    node_2 = NodeFirewallConfig(ip="172.18.10.2", hostname="ssh1",
                       output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                          "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                          "172.18.10.42",
                                          "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                          "172.18.10.11", "172.18.10.104"]),
                       input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                         "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                         "172.18.10.42",
                                         "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                         "172.18.10.11", "172.18.10.104"]),
                       forward_accept=set(), output_drop=set(), input_drop=set(), routes=set(), forward_drop=set(),
                       default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None
                       )
    node_3 = NodeFirewallConfig(ip="172.18.10.3", hostname="telnet1",
                           output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                              "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                              "172.18.10.42",
                                              "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                              "172.18.10.11", "172.18.10.104"]),
                           input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                             "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                             "172.18.10.42",
                                             "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                             "172.18.10.11", "172.18.10.104"]),
                           forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(), routes=set(),
                            default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_4 = NodeFirewallConfig(ip="172.18.10.21", hostname="honeypot1",
                           output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                                "172.18.10.79", "172.18.10.191", "172.18.10.10", "172.18.10.1", "172.18.10.254",
                                              "172.18.10.19", "172.18.10.31", "172.18.10.42",
                                              "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                              "172.18.10.11", "172.18.10.104"]),
                           input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                             "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                             "172.18.10.42",
                                             "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71", "172.18.10.11",
                                             "172.18.10.104"]),
                           forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(), routes=set(),
                           default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None
                           )
    node_5 = NodeFirewallConfig(ip="172.18.10.79", hostname="ftp1",
                           output_accept=set(
                               ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                "172.18.10.11", "172.18.10.104"]),
                           input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                             "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.19", "172.18.10.31",
                                             "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                             "172.18.10.11", "172.18.10.104"]),
                           forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(), routes=set(),
                           default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_6 = NodeFirewallConfig(ip="172.18.10.19", hostname="samba1",
                                output_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.31",
                                     "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75","172.18.10.71",
                                     "172.18.10.11", "172.18.10.104"]),
                                input_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.31",
                                     "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71",
                                     "172.18.10.11", "172.18.10.104"]),
                                forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                routes=set(),
                                default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_7 = NodeFirewallConfig(ip="172.18.10.31", hostname="shellshock1",
                                output_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.37",
                                     "172.18.10.82", "172.18.10.75", "172.18.10.71", "172.18.10.11",
                                     "172.18.10.104"]),
                                input_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.37",
                                     "172.18.10.82", "172.18.10.75", "172.18.10.71", "172.18.10.11",
                                     "172.18.10.104"]),
                                forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                routes=set(),
                                default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_8 = NodeFirewallConfig(ip="172.18.10.42", hostname="sql_injection1",
                                output_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.37",
                                     "172.18.10.82",
                                     "172.18.10.75", "172.18.10.71", "172.18.10.11",
                                     "172.18.10.104"]),
                                input_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.37",
                                     "172.18.10.82",
                                     "172.18.10.75", "172.18.10.71", "172.18.10.11",
                                     "172.18.10.104"]),
                                forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                routes=set(),
                                default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_9 = NodeFirewallConfig(ip="172.18.10.37", hostname="cve_2015_3306_1",
                                output_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.82",
                                     "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                input_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.82",
                                     "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                routes=set(),
                                default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_10 = NodeFirewallConfig(ip="172.18.10.82", hostname="cve_2015_1427_1",
                                output_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.37", "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                input_accept=set(
                                    ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                     "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                     "172.18.10.37",
                                     "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                routes=set(),
                                default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_11 = NodeFirewallConfig(ip="172.18.10.75", hostname="cve_2016_10033_1",
                                 output_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37", "172.18.10.82", "172.18.10.71", "172.18.10.11",
                                      "172.18.10.104"]),
                                 input_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37",
                                      "172.18.10.82", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                 forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                 routes=set(),
                                 default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_12 = NodeFirewallConfig(ip="172.18.10.71", hostname="cve_2010_0426_1",
                                 output_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.11", "172.18.10.104"]),
                                 input_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37",
                                      "172.18.10.82", "172.18.10.75", "172.18.10.11", "172.18.10.104"]),
                                 forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                 routes=set(),
                                 default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_13 = NodeFirewallConfig(ip="172.18.10.11", hostname="cve_2015_5602_1",
                                 output_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37", "172.18.10.82", "172.18.10.75", "172.18.10.71", "172.18.10.104"]),
                                 input_accept=set(
                                     ["172.18.10.2", "172.18.10.3", "172.18.10.21", "172.18.10.79", "172.18.10.191",
                                      "172.18.10.10", "172.18.10.1", "172.18.10.254", "172.18.10.79", "172.18.10.42",
                                      "172.18.10.37",
                                      "172.18.10.82", "172.18.10.75", "172.18.10.71", "172.18.10.104"]),
                                 forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                 routes=set(),
                                 default_input="DROP", default_output="DROP", default_forward="DROP", default_gw=None)
    node_14 = NodeFirewallConfig(ip="172.18.10.191", hostname="hacker_kali1",
                       output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                          "172.18.10.79", "172.18.10.191", "172.18.10.10", "172.18.10.1",
                                          "172.18.10.19", "172.18.10.31", "172.18.10.42", "172.18.10.37", "172.18.10.82",
                                          "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                       input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                         "172.18.10.79", "172.18.10.191", "172.18.10.10", "172.18.10.1",
                                         "172.18.10.19",
                                         "172.18.10.31", "172.18.10.42", "172.18.10.37", "172.18.10.82", "172.18.10.75",
                                         "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                       forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(), routes=set(),
                       default_input="DROP", default_output="DROP", default_forward="DROP", default_gw="172.18.10.10")
    node_15 = NodeFirewallConfig(ip="172.18.10.254", hostname="client1",
                                 output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                                    "172.18.10.79", "172.18.10.10", "172.18.10.1",
                                                    "172.18.10.254",
                                                    "172.18.10.19", "172.18.10.31", "172.18.10.42", "172.18.10.37",
                                                    "172.18.10.82",
                                                    "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                 input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                                   "172.18.10.79", "172.18.10.10", "172.18.10.1",
                                                   "172.18.10.254",
                                                   "172.18.10.19",
                                                   "172.18.10.31", "172.18.10.42", "172.18.10.37", "172.18.10.82",
                                                   "172.18.10.75",
                                                   "172.18.10.71", "172.18.10.11", "172.18.10.104"]),
                                 forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                 routes=set(),
                                 default_input="DROP", default_output="DROP", default_forward="DROP",
                                 default_gw="172.18.10.10")
    node_16 = NodeFirewallConfig(ip="172.18.10.104", hostname="pengine_exploit1",
                                 output_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                                    "172.18.10.79", "172.18.10.10", "172.18.10.1",
                                                    "172.18.10.254",
                                                    "172.18.10.19", "172.18.10.31", "172.18.10.42", "172.18.10.37",
                                                    "172.18.10.82",
                                                    "172.18.10.75", "172.18.10.71", "172.18.10.11", "172.18.10.104",
                                                    "172.18.10.191"]),
                                 input_accept=set(["172.18.10.2", "172.18.10.3", "172.18.10.21",
                                                   "172.18.10.79", "172.18.10.10", "172.18.10.1",
                                                   "172.18.10.254",
                                                   "172.18.10.19",
                                                   "172.18.10.31", "172.18.10.42", "172.18.10.37", "172.18.10.82",
                                                   "172.18.10.75",
                                                   "172.18.10.71", "172.18.10.11", "172.18.10.104", "172.18.10.191"]),
                                 forward_accept=set(), output_drop=set(), input_drop=set(), forward_drop=set(),
                                 routes=set(),
                                 default_input="DROP", default_output="DROP", default_forward="DROP",
                                 default_gw="172.18.10.10")
    node_configs = [node_1, node_2, node_3, node_4, node_5, node_6, node_7, node_8, node_9, node_10, node_11, node_12,
                    node_13, node_14, node_15, node_16]
    topology = Topology(node_configs=node_configs, subnetwork = "172.18.10.0/24")
    return topology


if __name__ == '__main__':
    if not os.path.exists(util.default_topology_path()):
        TopologyGenerator.write_topology(default_topology())
    topology = util.read_topology(util.default_topology_path())
    emulation_config = EmulationConfig(agent_ip="172.18.10.191", agent_username=constants.PYCR_ADMIN.USER,
                                     agent_pw=constants.PYCR_ADMIN.PW, server_connection=False)
    TopologyGenerator.create_topology(topology=topology, emulation_config=emulation_config)