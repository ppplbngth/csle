from typing import List, Dict, Any
import time
from csle_common.dao.emulation_action.defender.emulation_defender_action_type import EmulationDefenderActionType
from csle_common.dao.emulation_action.defender.emulation_defender_action_id import EmulationDefenderActionId
from csle_common.dao.emulation_action.defender.emulation_defender_action_outcome import EmulationDefenderActionOutcome


class EmulationDefenderAction:
    """
    Class representing an action of the defender in the environment
    """

    def __init__(self, id: EmulationDefenderActionId, name: str, cmds: List[str],
                 type: EmulationDefenderActionType, descr: str,
                 ips: List[str], index: int,
                 action_outcome: EmulationDefenderActionOutcome = EmulationDefenderActionOutcome.GAME_END,
                 alt_cmds: List[str] = None, execution_time: float = 0.0, ts: float = 0.0):
        """
        Class constructor

        :param id: id of the action
        :param name: name of the action
        :param cmds: command-line commands to apply the action on the emulation
        :param type: type of the action
        :param descr: description of the action (documentation)
        :param ips: ip of the machine to apply the action to
        :param index: index of the machine to apply the action to
        :param action_outcome: type of the outcome of the action
        :param alt_cmds: alternative command if the first command does not work
        :param execution_time: the time it took to run the action
        :param ts: the timestamp the action was run
        """
        self.id = id
        self.name = name
        self.cmds = cmds
        self.type = type
        self.descr = descr
        self.ips = ips
        self.action_outcome = action_outcome
        self.alt_cmds = alt_cmds
        self.index = index
        self.ts = ts
        self.execution_time = execution_time

    def __str__(self) -> str:
        """
        :return: a string representation of the object
        """
        return "id:{},name:{},ips:{},index:{}".format(self.id, self.name, self.ips, self.index)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "EmulationDefenderAction":
        """
        Converts a dict representation to an instance

        :param d: the dict to convert
        :return: the instance
        """
        obj = EmulationDefenderAction(
            id=d["id"], name=d["name"], cmds=d["cmds"], type=d["type"], descr=d["descr"],
            ips=d["ips"],
            index=d["index"], action_outcome=d["action_outcome"], alt_cmds=d["alt_cmds"],
            ts=d["ts"])
        return obj

    def to_dict(self) -> Dict[str, Any]:
        """
        :return: a dicr representation of the object
        """
        d = {}
        d["id"] = self.id
        d["name"] = self.name
        d["cmds"] = self.cmds
        d["type"] = self.type
        d["descr"] = self.descr
        d["ips"] = self.ips
        d["index"] = self.index
        d["action_outcome"] = self.action_outcome
        d["alt_cmds"] = self.alt_cmds
        d["execution_time"] = self.execution_time
        d["ts"] = self.ts
        return d

    def ips_match(self, ips: List[str]) -> bool:
        """
        Checks if a list of ips overlap with the ips of this host

        :param ips: the list of ips to check
        :return:  True if they match, False otherwise
        """
        for ip in self.ips:
            if ip in ips:
                return True
        return False

    def to_kafka_record(self) -> str:
        """
        Converts the instance into a kafka record format

        :param total_time: the total time of execution
        :return: the kafka record
        """
        ts = time.time()
        record = f"{ts},{self.id},{self.descr},{self.index},{self.name}," \
                 f"{self.execution_time},{'_'.join(self.ips)},{'_'.join(self.cmds)},{self.type}," \
                 f"{self.action_outcome},{'_'.join(self.alt_cmds)}"
        return record

    @staticmethod
    def from_kafka_record(record: str) -> "EmulationDefenderAction":
        """
        Converts a kafka record into an instance

        :param record: the record to convert
        :return: the created instance
        """
        parts = record.split(",")
        obj = EmulationDefenderAction(id=EmulationDefenderActionId(int(parts[1])), ts=float(parts[0]),
                                      descr=parts[2], index=int(parts[3]),
                                      name=parts[4],
                                      execution_time=float(parts[5]), ips=parts[6].split("_"),
                                      cmds=parts[7].split("_"),
                                      type=EmulationDefenderActionType(int(parts[8])),
                                      action_outcome=EmulationDefenderActionOutcome(int(parts[9])),
                                      alt_cmds=parts[10].split("_"))
        return obj

    def to_json_str(self) -> str:
        """
        Converts the DTO into a json string

        :return: the json string representation of the DTO
        """
        import json
        json_str = json.dumps(self.to_dict(), indent=4, sort_keys=True)
        return json_str

    def to_json_file(self, json_file_path: str) -> None:
        """
        Saves the DTO to a json file

        :param json_file_path: the json file path to save  the DTO to
        :return: None
        """
        import io
        json_str = self.to_json_str()
        with io.open(json_file_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

    def copy(self) -> "EmulationDefenderAction":
        """
        :return: a copy of the DTO
        """
        return EmulationDefenderAction.from_dict(self.to_dict())

    def num_attributes(self) -> int:
        """
        :return: The number of attributes of the DTO
        """
        return 11

    @staticmethod
    def schema() -> "EmulationDefenderAction":
        """
        :return: get the schema of the DTO
        """
        return EmulationDefenderAction(id=EmulationDefenderActionId.STOP, name="", cmds=[""],
                                       type=EmulationDefenderActionType.STOP, descr="", ips=[""], index=-1,
                                       action_outcome=EmulationDefenderActionOutcome.GAME_END, alt_cmds=[""],
                                       execution_time=0.0, ts=0.0)
