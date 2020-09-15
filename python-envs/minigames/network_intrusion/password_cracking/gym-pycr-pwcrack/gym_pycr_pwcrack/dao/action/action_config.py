from typing import List
import gym
from gym_pycr_pwcrack.dao.action.action import Action
from gym_pycr_pwcrack.dao.action.action_type import ActionType
import gym_pycr_pwcrack.constants.constants as constants
from gym_pycr_pwcrack.dao.action.action_id import ActionId

class ActionConfig:

    def __init__(self, actions: List[Action]):
        self.actions = actions
        self.num_actions = len(self.actions)
        self.action_space = gym.spaces.Discrete(self.num_actions)
        self.action_lookup_d = {}
        for action in actions:
            self.action_lookup_d[action.id] = action

class NMAPActions:

    @staticmethod
    def TCP_SYN_STEALTH_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.TCP_SYN_STEALTH_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TCP_SYN_STEALTH_SCAN_SUBNET
        cmd = "nmap -sS " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " \
              + str(id) + ".xml " + ip
        return Action(id=id, name="TCP SYN (Stealth) Scan", cmd=cmd,
                      type=ActionType.RECON,
                      descr="A stealthy and fast TCP SYN scan to detect open TCP ports on the subnet",
                      cost=1.6*cost_noise_multiplier, noise=2*cost_noise_multiplier,
                      ip=ip, subnet=subnet)

    @staticmethod
    def PING_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.PING_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.PING_SCAN_SUBNET
        cmd = "nmap -sP " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="Ping Scan", cmd=cmd,
               type=ActionType.RECON,
               descr="A host discovery scan, it is quick because it only checks of hosts are up with Ping, without "
                     "scanning the ports.",
               cost=1*cost_noise_multiplier, noise=1*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def UDP_PORT_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.UDP_PORT_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.UDP_PORT_SCAN_SUBNET
        cmd = "nmap -sU -p-" + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + \
              str(id) + ".xml" + " "+ ip
        return Action(id=id, name="UDP Port Scan", cmd=cmd,
               type=ActionType.RECON,
               descr="",
               cost=2*cost_noise_multiplier, noise=3*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def TCP_CON_NON_STEALTH_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.TCP_CON_NON_STEALTH_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TCP_CON_NON_STEALTH_SCAN_SUBNET
        cmd = "nmap -sT -p-" + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="TCP Connection (Non-Stealth) Scan", cmd=cmd,
               type=ActionType.RECON,
               descr="A non-stealthy and fast TCP SYN scan to detect open TCP ports on the subnet",
               cost=6*cost_noise_multiplier, noise=5*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def TCP_FIN_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.TCP_FIN_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TCP_FIN_SCAN_SUBNET
        cmd = "nmap -sF " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="FIN Scan",
               cmd=cmd,
               type=ActionType.RECON,
               descr="A special type of TCP port scan using FIN, can avoid IDS and firewalls that block SYN scans",
               cost=2*cost_noise_multiplier, noise=3*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def TCP_NULL_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.TCP_NULL_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TCP_NULL_SCAN_SUBNET
        cmd = "nmap -sN " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="Null Scan",
               cmd=cmd,
               type=ActionType.RECON,
               descr="A special type of TCP port scan using Null, can avoid IDS and firewalls that block SYN scans",
               cost=2*cost_noise_multiplier, noise=3*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def TCP_XMAS_TREE_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.TCP_XMAS_TREE_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TCP_XMAS_TREE_SCAN_SUBNET
        cmd = "nmap -sX " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="Xmas Tree Scan",
               cmd=cmd, type=ActionType.RECON,
               descr="A special type of TCP port scan using XMas Tree, "
                     "can avoid IDS and firewalls that block SYN scans",
               cost=2*cost_noise_multiplier, noise=3*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def OS_DETECTION_SCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.OS_DETECTION_SCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.OS_DETECTION_SCAN_SUBNET
        cmd = "nmap -O --osscan-guess --max-os-tries 1 " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="OS detection scan",
               cmd=cmd, type=ActionType.RECON,
               descr="OS detection/guess scan",
               cost=4*cost_noise_multiplier, noise=4*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def VULSCAN(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.VULSCAN_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.VULSCAN_SUBNET
        cmd = "nmap -sV --script=vulscan/vulscan.nse " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="vulscan.nse vulnerability scanner",
               cmd=cmd, type=ActionType.RECON,
               descr="Uses a vulcan.nse script to turn NMAP into a vulnerability scanner",
               cost=173*cost_noise_multiplier, noise=5*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def NMAP_VULNERS(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        id = ActionId.NMAP_VULNERS_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.NMAP_VULNERS_SUBNET
        cmd = "nmap -sV --script vulners.nse " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " \
              + str(id) + ".xml " + ip
        return Action(id=id, name="nmap_vulners vulnerability scanner",
               cmd=cmd, type=ActionType.RECON,
               descr="Uses vulners.nse script to turn NMAP into a vulnerability scanner",
               cost=170*cost_noise_multiplier, noise=5*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def TELNET_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        telnet_args = constants.NMAP.TELNET_BRUTE_HOST
        id = ActionId.TELNET_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.TELNET_SAME_USER_PASS_DICTIONARY_SUBNET
            telnet_args = constants.NMAP.TELNET_BRUTE_SUBNET
        cmd = "nmap " + telnet_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + \
              str(id) + ".xml " + ip
        return Action(id=id, name="Telnet dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames "
                     "for Telnet where username=password",
               cost=49*cost_noise_multiplier, noise=6*cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def SSH_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        ssh_args = constants.NMAP.SSH_BRUTE_HOST
        id = ActionId.SSH_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.SSH_SAME_USER_PASS_DICTIONARY_SUBNET
            ssh_args = constants.NMAP.SSH_BRUTE_SUBNET
        cmd = "nmap " + ssh_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " + \
              str(id) + ".xml " + ip
        return Action(id=id, name="SSH dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                      "for SSH where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def FTP_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        ftp_args = constants.NMAP.FTP_BRUTE_HOST
        id = ActionId.FTP_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.FTP_SAME_USER_PASS_DICTIONARY_SUBNET
            ftp_args = constants.NMAP.FTP_BRUTE_SUBNET
        cmd = "nmap " + ftp_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="FTP dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for FTP where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def CASSANDRA_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        cassandra_args = constants.NMAP.CASSANDRA_BRUTE_HOST
        id = ActionId.CASSANDRA_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.CASSANDRA_SAME_USER_PASS_DICTIONARY_SUBNET
            cassandra_args = constants.NMAP.CASSANDRA_BRUTE_SUBNET
        cmd = "nmap " + cassandra_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="Cassandra dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for Cassandra where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def IRC_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        irc_args = constants.NMAP.IRC_BRUTE_HOST
        id = ActionId.IRC_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            id = ActionId.IRC_SAME_USER_PASS_DICTIONARY_SUBNET
            irc_args = constants.NMAP.IRC_BRUTE_SUBNET
        cmd = "nmap " + irc_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="IRC dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for IRC where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def MONGO_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        mongo_args = constants.NMAP.MONGO_BRUTE_HOST
        id = ActionId.MONGO_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            mongo_args = constants.NMAP.MONGO_BRUTE_SUBNET
            id = ActionId.MONGO_SAME_USER_PASS_DICTIONARY_SUBNET
        cmd = "nmap " + mongo_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS + " " \
              + str(id) + ".xml " + ip
        return Action(id=id, name="MongoDB dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for MongoDB where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def MYSQL_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        mysql_args = constants.NMAP.MYSQL_BRUTE_HOST
        id = ActionId.MYSQL_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            mysql_args = constants.NMAP.MYSQL_BRUTE_SUBNET
            id = ActionId.MYSQL_SAME_USER_PASS_DICTIONARY_SUBNET
        cmd = "nmap " + mysql_args + " " + constants.NMAP.SPEED_ARGS + " " \
              + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="MySQL dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for MySQL where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def SMTP_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        smtp_args = constants.NMAP.SMTP_BRUTE_HOST
        id = ActionId.SMTP_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            smtp_args = constants.NMAP.SMTP_BRUTE_SUBNET
            id = ActionId.SMTP_SAME_USER_PASS_DICTIONARY_SUBNET
        cmd = "nmap " + smtp_args + " " + constants.NMAP.SPEED_ARGS + " " + constants.NMAP.FILE_ARGS \
              + " " + str(id) + ".xml " + ip
        return Action(id=id, name="SMTP dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for SMTP where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)

    @staticmethod
    def POSTGRES_SAME_USER_PASS_DICTIONARY(ip:str, subnet=True) -> Action:
        cost_noise_multiplier = 1
        postgres_args = constants.NMAP.POSTGRES_BRUTE_HOST
        id = ActionId.POSTGRES_SAME_USER_PASS_DICTIONARY_HOST
        if subnet:
            cost_noise_multiplier = 10
            postgres_args = constants.NMAP.POSTGRES_BRUTE_SUBNET
            id = ActionId.POSTGRES_SAME_USER_PASS_DICTIONARY_SUBNET
        cmd = "nmap " + postgres_args + " " + constants.NMAP.SPEED_ARGS + " " \
              + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml " + ip
        return Action(id=id, name="Postgres dictionary attack for username=pw",
               cmd=cmd, type=ActionType.RECON,
               descr="A dictionary attack that tries common passwords and usernames"
                     "for Postgres where username=password",
               cost=49 * cost_noise_multiplier, noise=6 * cost_noise_multiplier,
               ip=ip, subnet=subnet)


# class HYDRAActions:
#     @staticmethod
#     def TELNET_SAME_USER_PASS_DICTIONARY(ip):
#         return Action(id=11, name="Telnet dictionary attack for username=pw ",
#                       cmd="hydra -L " + constants.SECLISTS.TOP_USERNAMES_SHORTLIST + " -P "
#                           + constants.SECLISTS.TOP_USERNAMES_SHORTLIST
#                           + " 172.18.1.3 telnet -V -f" + constants.NMAP.FILE_ARGS + " " + str(id) + ".xml" + " "
#                           + ip,
#                       type=ActionType.RECON,
#                       descr="A dictionary attack that tries common passwords and usernames "
#                             "for Telnet where username=password",
#                       cost=1.6, noise=2)