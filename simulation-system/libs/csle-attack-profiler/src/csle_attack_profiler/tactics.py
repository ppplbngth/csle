"""
Type of tactics that can be used by the attacker
"""
from enum import Enum

class Tactics(Enum):
    RECONNAISSANCE = "reconnaissance"
    RESOURCE_DEVELOPMENT = "resource-development"
    INITIAL_ACCESS = "initial-access"
    EXECUTION = "execution"
    PERSISTANCE = "persistance"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    DEFENSE_EVASION = "defense-evasion"
    CREDENTIAL_ACCESS = "credential-access"
    DISCOVERY = "discover"
    LATERAL_MOVEMENT = "lateral-movement"
    COLLECTION = "collection"
    COMMAND_AND_CONTROL = "command-and-control"
    EXFILTRATION = "exfiltration"
    IMPACT = "impact"

    @staticmethod
    def get_tactics(id):

        mapping = {
            Tactics.RECONNAISSANCE: {"techniques": {"Active Scanning", "Gather Victim Host Information", "Network Service Discovery"}},
            Tactics.PRIVILEGE_ESCALATION: {"techniques": ["Abuse Elevation Control Mechanism"]}
        }
        return mapping.get(id, None)

