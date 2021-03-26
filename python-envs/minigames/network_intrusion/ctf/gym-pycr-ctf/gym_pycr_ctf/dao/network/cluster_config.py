from typing import List
import paramiko
import time
import gym_pycr_ctf.constants.constants as constants
from gym_pycr_ctf.dao.action_results.action_costs import ActionCosts
from gym_pycr_ctf.dao.action.action import Action
from gym_pycr_ctf.dao.action.action_id import ActionId
from gym_pycr_ctf.dao.action_results.action_alerts import ActionAlerts

class ClusterConfig:
    """
    DTO with data for connecting to the cluster and executing commands
    """

    def __init__(self, agent_ip : str,  agent_username: str, agent_pw : str,
                 server_ip: str = None,
                 server_connection : bool = False,
                 server_private_key_file : str = None, server_username : str = None,
                 warmup = False, warmup_iterations :int = 500, port_forward_next_port : int = 4000):
        self.agent_ip = agent_ip
        self.agent_username = agent_username
        self.agent_pw = agent_pw
        self.server_ip = server_ip
        self.server_connection = server_connection
        self.server_private_key_file = server_private_key_file
        self.server_username = server_username
        self.server_conn = None
        self.agent_conn = None
        self.relay_channel = None
        self.cluster_services = []
        self.cluster_cves = []
        self.warmup = warmup
        self.warmup_iterations = warmup_iterations
        self.port_forward_next_port = port_forward_next_port
        self.ids_router = False
        self.ids_router_ip = ""
        self.router_conn = None
        self.skip_exploration = False

    def connect_server(self):
        """
        Creates a connection to a server that can work as a jumphost

        :return:
        """
        if not self.server_connection:
            raise ValueError("Server connection not enabled, cannot connect to server")
        if self.server_private_key_file is None:
            raise ValueError("Server private key file is not specified, cannot connect to server")
        if self.server_ip is None:
            raise ValueError("Server ip not specified, cannot connect to server")
        if self.server_username is None:
            raise ValueError("Server username not specified, cannot connect to server")
        key = paramiko.RSAKey.from_private_key_file(self.server_private_key_file)
        server_conn = paramiko.SSHClient()
        server_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        server_conn.connect(self.server_ip, username=self.server_username, pkey=key)
        self.server_conn = server_conn

    def connect_router(self):
        print("Connecting to router host..")
        agent_addr = (self.agent_ip, 22)
        target_addr = (self.ids_router_ip, 22)
        agent_transport = self.agent_conn.get_transport()
        relay_channel = agent_transport.open_channel(constants.SSH.DIRECT_CHANNEL, target_addr, agent_addr,
                                                     timeout=3)
        router_conn = paramiko.SSHClient()
        router_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        router_conn.connect(self.ids_router_ip, username="pycr_admin", password="pycr@admin-pw_191",
                            sock=relay_channel, timeout=3)
        self.router_conn = router_conn
        print("Router host connected successfully")


    def connect_agent(self):
        """
        Connects to the agent's host with SSH, either directly or through a jumphost

        :return: None
        """
        print("Connecting to agent host..")

        # Connect to agent using server as a jumphost
        if self.server_connection:
            if self.server_conn is None:
                self.connect_server()
            server_transport = self.server_conn.get_transport()
            agent_addr = (self.agent_ip, 22)
            server_addr = (self.server_ip, 22)

            relay_channel = server_transport.open_channel(constants.SSH.DIRECT_CHANNEL, agent_addr, server_addr)
            self.relay_channel = relay_channel
            agent_conn = paramiko.SSHClient()
            agent_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            agent_conn.connect(self.agent_ip, username=self.agent_username, password=self.agent_pw, sock=relay_channel)
            self.agent_conn = agent_conn
            self.agent_channel = self.agent_conn.invoke_shell()


        # Connect directly to agent with ssh
        else:
            agent_conn = paramiko.SSHClient()
            agent_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            agent_conn.connect(self.agent_ip, username=self.agent_username, password=self.agent_pw)
            self.agent_conn = agent_conn
            self.agent_channel = self.agent_conn.invoke_shell()

        print("Agent host connected successfully")

        if self.ids_router and self.ids_router_ip != "":
            self.connect_router()

        # self._su_root()
        #
        # print("Root access")


    def _su_root(self) -> None:
        """
        Uses an interactive channel to change to root account

        :return: None
        """

        # clear output
        if self.agent_channel.recv_ready():
            output = self.agent_channel.recv(constants.COMMON.DEFAULT_RECV_SIZE)

        self.agent_channel.send(constants.COMMANDS.CHANNEL_SU_ROOT)
        time.sleep(0.2)
        self.agent_channel.send(constants.COMMANDS.CHANNEL_ROOT)
        time.sleep(0.2)

        # clear output
        if self.agent_channel.recv_ready():
            output = self.agent_channel.recv(constants.COMMON.DEFAULT_RECV_SIZE)

        self.agent_channel.send(constants.COMMANDS.CHANNEL_WHOAMI)
        time.sleep(0.2)
        if self.agent_channel.recv_ready():
            output = self.agent_channel.recv(constants.COMMON.DEFAULT_RECV_SIZE)
            output_str = output.decode("utf-8")
            assert "root" in output_str


    def download_cluster_services(self) -> None:
        """
        Downloads a list of services from the server to populate the lookup table

        :return: None
        """
        print("Downloading cluster services...")
        sftp_client = self.agent_conn.open_sftp()
        remote_file = sftp_client.open(constants.COMMON.SERVICES_FILE)
        cluster_services = []
        try:
            for line in remote_file:
                if not line.startswith("#"):
                    service = line.split(" ", 1)[0]
                    service = service.split("\t", 1)[0]
                    cluster_services.append(service)
        finally:
            remote_file.close()
        self.cluster_services = cluster_services
        print("{} services downloaded successfully".format(len(self.cluster_services)))


    def download_cves(self) -> None:
        """
        Downloads a list of CVEs from the server to populate the lookup table

        :return: None
        """
        print("Downloading CVEs...")
        sftp_client = self.agent_conn.open_sftp()
        remote_file = sftp_client.open(constants.COMMON.CVE_FILE, "r")
        cves = []
        try:
            start = time.time()
            for line in remote_file:
                cves.append(line.replace("\n",""))
            end = time.time()
        finally:
            remote_file.close()
        self.cluster_cves = cves
        print("{} cves downloaded successfully in {}s".format(len(self.cluster_cves), end - start))


    def close(self) -> None:
        """
        Closes the cluster connection

        :return: None
        """
        if self.agent_conn is not None:
            self.agent_conn.close()
            self.agent_conn = None
        if self.relay_channel is not None:
            self.relay_channel.close()
            self.relay_channel = None
        if self.server_conn is not None:
            self.server_conn.close()
            self.server_conn = None


    def load_action_costs(self, actions: List[Action], dir: str, nmap_ids: List[ActionId],
                          network_service_ids: List[ActionId], shell_ids: List[ActionId],
                          nikto_ids: List[ActionId], masscan_ids: List[ActionId],
                          action_lookup_d_val: dict) -> ActionCosts:
        """
        Loads measured action costs from the cluster

        :param actions: list of actions
        :param nmap_ids: list of ids of nmap actions
        :param network_service_ids: list of ids of network service actions
        :param shell_ids: list of ids of shell actions
        :param nikto_ids: list of ids of nikto actions
        :param masscan_ids: list of ids of masscan actions
        :param action_lookup_d_val: dict for converting action id to action
        :return: action costs
        """
        print("Loading action costs from cluster..")
        action_costs = ActionCosts()
        sftp_client = self.agent_conn.open_sftp()

        # Load Nmap costs
        cmd = constants.COMMANDS.LIST_CACHE + dir + " | grep _cost"
        stdin, stdout, stderr = self.agent_conn.exec_command(cmd)
        file_list = []
        for line in stdout:
            line_str = line.replace("\n", "")
            file_list.append(line_str)

        nmap_id_values = list(map(lambda x: x.value, nmap_ids))
        masscan_id_values = list(map(lambda x: x.value, masscan_ids))
        nikto_id_values = list(map(lambda x: x.value, nikto_ids))
        nmap_id_values = nmap_id_values+masscan_id_values+nikto_ids
        network_service_actions_id_values = list(map(lambda x: x.value, network_service_ids))
        remote_file = None
        for file in file_list:
            parts = file.split("_")
            id = int(parts[0])
            if id in nmap_id_values:
                try:
                    idx = parts[1]
                    a = action_lookup_d_val[(int(id), int(idx))]
                    ip = parts[2]
                    remote_file = sftp_client.open(file, mode="r")
                    cost_str = remote_file.read()
                    cost = round(float(cost_str), 1)
                    action_costs.add_cost(action_id=a.id, ip=ip, cost=cost)
                    a.cost = cost
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

            elif id in network_service_actions_id_values:
                try:
                    idx = parts[1]
                    a = action_lookup_d_val[(int(id), int(idx))]
                    ip = parts[2]
                    remote_file = None
                    remote_file = sftp_client.open(file, mode="r")
                    cost_str = remote_file.read()
                    cost = round(float(cost_str),1)
                    action_costs.service_add_cost(action_id=a.id, ip=a.ip, cost=cost)
                    a.cost = cost
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

        # Load shell action costs which are user and service specific
        shell_actions = list(filter(lambda x: x.id in shell_ids, actions))
        shell_id_values = list(map(lambda x: x.value, shell_ids))
        cmd = constants.COMMANDS.LIST_CACHE + dir + " | grep _cost"
        stdin, stdout, stderr = self.agent_conn.exec_command(cmd)
        file_list = []
        for line in stdout:
            line_str = line.replace("\n", "")
            if "_cost" in line_str:
                file_list.append(line_str)
        for file in file_list:
            parts = file.split("_")
            id = int(parts[0])
            if id in shell_id_values:
                try:
                    parts = file.split("_")
                    idx = parts[1]
                    ip = parts[2]
                    service = parts[3]
                    user = self.extract_username(parts=parts, idx=4, terminal_key="_cost")
                    remote_file = None
                    remote_file = sftp_client.open(file, mode="r")
                    cost_str = remote_file.read()
                    cost = round(float(cost_str), 1)
                    a = action_lookup_d_val[(int(id), int(idx))]
                    action_costs.find_add_cost(action_id=a.id, ip=ip, cost=cost, user=user, service=service)
                    a.cost = cost
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

        # Load user command action costs which are user specific
        cmd = constants.COMMANDS.LIST_CACHE + dir + " | grep _cost"
        stdin, stdout, stderr = self.agent_conn.exec_command(cmd)
        file_list = []
        for line in stdout:
            line_str = line.replace("\n", "")
            if "_cost" in line_str:
                file_list.append(line_str)
        for file in file_list:
            parts = file.split("_")
            id = int(parts[0])
            if id in shell_id_values:
                try:
                    parts = file.split("_")
                    idx = parts[1]
                    ip = parts[2]
                    service = parts[3]
                    user = self.extract_username(parts=parts, idx=4, terminal_key="_cost")
                    remote_file = None
                    remote_file = sftp_client.open(file, mode="r")
                    cost_str = remote_file.read()
                    cost = round(float(cost_str), 1)
                    action_costs.install_add_cost(action_id=id, ip=ip, cost=cost, user=user)
                    a.cost = cost
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

        print("Successfully loaded {} action costs from cluster".format(len(action_costs.costs) +
                                                                        len(action_costs.find_costs) +
                                                                        len(action_costs.service_costs) +
                                                                        len(action_costs.install_costs) +
                                                                        len(action_costs.pivot_scan_costs)))
        return action_costs

    def load_action_alerts(self, actions: List[Action], dir: str, action_ids: List[ActionId],
                           shell_ids: List[ActionId],
                          action_lookup_d_val: dict) -> ActionCosts:
        print("Loading action alerts from cluster..")
        action_alerts = ActionAlerts()
        sftp_client = self.agent_conn.open_sftp()

        # Load alerts
        cmd = constants.COMMANDS.LIST_CACHE + dir + " | grep _alerts"
        stdin, stdout, stderr = self.agent_conn.exec_command(cmd)
        file_list = []
        for line in stdout:
            line_str = line.replace("\n", "")
            file_list.append(line_str)

        action_ids = list(filter(lambda x: x not in shell_ids, action_ids))
        action_id_values = list(map(lambda x: x.value, action_ids))
        shell_id_values = list(map(lambda x: x.value, shell_ids))
        remote_file = None
        for file in file_list:
            parts = file.split("_")
            id = int(parts[0])
            if id in action_id_values:
                try:
                    idx = parts[1]
                    a = action_lookup_d_val[(int(id), int(idx))]
                    ip = parts[2]
                    if ip == "alerts.txt":
                        ip = a.ip
                    remote_file = sftp_client.open(file, mode="r")
                    alerts_str = remote_file.read().decode()
                    alerts_parts = alerts_str.split(",")
                    sum_priorities = int(alerts_parts[0])
                    num_alerts = int(alerts_parts[1])
                    action_alerts.add_alert(action_id=a.id, ip=ip, alert = (sum_priorities, num_alerts))
                    a.alerts = (sum_priorities, num_alerts)
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

        # Load shell action costs which are user and service specific
        shell_actions = list(filter(lambda x: x.id in shell_ids, actions))
        shell_id_values = list(map(lambda x: x.value, shell_ids))

        cmd = constants.COMMANDS.LIST_CACHE + dir + " | grep _alerts"
        stdin, stdout, stderr = self.agent_conn.exec_command(cmd)
        file_list = []
        for line in stdout:
            line_str = line.replace("\n", "")
            if "_alerts" in line_str:
                file_list.append(line_str)
        for file in file_list:
            parts = file.split("_")
            id = int(parts[0])
            if id in shell_id_values:
                try:
                    parts = file.split("_")
                    idx = parts[1]
                    ip = parts[2]
                    service = parts[3]
                    user = self.extract_username(parts=parts, idx=4, terminal_key="_alerts")
                    remote_file = None
                    remote_file = sftp_client.open(file, mode="r")
                    alerts_str = remote_file.read().decode()
                    alerts_parts = alerts_str.split(",")
                    sum_priorities = int(alerts_parts[0])
                    num_alerts = int(alerts_parts[1])
                    alert = (sum_priorities, num_alerts)
                    a = action_lookup_d_val[(int(id), int(idx))]
                    action_alerts.user_ip_add_alert(action_id=a.id, ip=ip, alert=alert, user=user, service=service)
                    a.alerts = alert
                except Exception as e:
                    print("{}".format(str(e)))
                finally:
                    if remote_file is not None:
                        remote_file.close()

        print("Successfully loaded {} action alerts from cluster".format(len(action_alerts.alerts) +
                                                                        len(action_alerts.user_ip_alerts) +
                                                                        len(action_alerts.pivot_scan_alerts)))

        return action_alerts


    def extract_username(self, parts : List[str], idx :int, terminal_key: str) -> str:
        rest = "_".join(parts[idx:])
        parts2 = rest.split(terminal_key)
        return parts2[0]