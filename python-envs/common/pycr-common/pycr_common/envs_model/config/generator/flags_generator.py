import random
from pycr_common.dao.container_config.vulnerabilities_config import VulnerabilitiesConfig
from pycr_common.dao.container_config.node_flags_config import NodeFlagsConfig
from pycr_common.dao.container_config.flags_config import FlagsConfig
from pycr_common.dao.container_config.vulnerability_type import VulnType
from pycr_common.util.experiments_util import util
from pycr_common.dao.network.emulation_config import EmulationConfig
from pycr_common.envs_model.logic.emulation.util.common.emulation_util import EmulationUtil
from pycr_common.envs_model.config.generator.generator_util import GeneratorUtil
import pycr_common.constants.constants as constants


class FlagsGenerator:
    """
    A Utility Class for generating flag configuration files
    """

    @staticmethod
    def generate(vuln_cfg: VulnerabilitiesConfig, num_flags) -> FlagsConfig:
        """
        Generates a flag configuration according to a specific vulnerabilities config and number of flags

        :param vuln_cfg: the vulnerabilities config
        :param num_flags: the number of flags
        :return: The created flags configuration
        """
        vulnerabilities = vuln_cfg.vulnerabilities
        random.shuffle(vulnerabilities)
        flag_cfgs = []

        if num_flags > len(vulnerabilities):
            raise AssertionError("Too few vulnerable nodes")

        for i in range(num_flags):
            if vulnerabilities[i].vuln_type == VulnType.WEAK_PW:
                flag_dirs = [constants.COMMANDS.SLASH_DELIM + constants.COMMANDS.TMP_DIR +
                             constants.COMMANDS.SLASH_DELIM,
                             constants.COMMANDS.SLASH_DELIM + constants.COMMANDS.HOME_DIR +
                             constants.COMMANDS.SLASH_DELIM + vulnerabilities[i].username +
                             constants.COMMANDS.SLASH_DELIM]
            else:
                flag_dirs = [constants.COMMANDS.SLASH_DELIM + constants.COMMANDS.TMP_DIR +
                             constants.COMMANDS.SLASH_DELIM]
            dir_idx = random.randint(0, len(flag_dirs)-1)
            flag_dir = flag_dirs[dir_idx]
            flag_name = "flag" + str(i)
            filename = flag_name + constants.FILE_PATTERNS.TXT_FILE_SUFFIX
            flags = [(flag_dir + filename, flag_name, flag_dir, i, True, 1)]
            flag_cfg = NodeFlagsConfig(ip=vulnerabilities[i].node_ip, flags=flags)
            flag_cfgs.append(flag_cfg)

        fl_cfg = FlagsConfig(flags = flag_cfgs)

        return fl_cfg

    @staticmethod
    def create_flags(flags_config: FlagsConfig, emulation_config: EmulationConfig) -> None:
        """
        Connects to a node in the emulation and creates the flags according to a given flags config

        :param flags_config: the flags config
        :param emulation_config: the emulation config
        :return: None
        """
        for flags_conf in flags_config.flags:
            GeneratorUtil.connect_admin(emulation_config=emulation_config, ip=flags_conf.ip)

            for flag in flags_conf.flags:
                path, content, dir, id, requires_root, score = flag
                cmd = constants.COMMANDS.SUDO_RM_RF + " {}".format(path)
                EmulationUtil.execute_ssh_cmd(cmd=cmd, conn=emulation_config.agent_conn)
                cmd = constants.COMMANDS.SUDO_TOUCH + " {}".format(path)
                EmulationUtil.execute_ssh_cmd(cmd=cmd, conn=emulation_config.agent_conn)
                cmd = constants.COMMANDS.ECHO + " '{}' >> {}".format(content, path)
                EmulationUtil.execute_ssh_cmd(cmd=cmd, conn=emulation_config.agent_conn)

            GeneratorUtil.disconnect_admin(emulation_config=emulation_config)


    @staticmethod
    def write_flags_config(flags_config: FlagsConfig, path: str = None) -> None:
        """
        Writes the default configuration to a json file

        :param path: the path to write the configuration to
        :return: None
        """
        path = util.default_flags_path(out_dir=path)
        util.write_flags_config_file(flags_config, path)

