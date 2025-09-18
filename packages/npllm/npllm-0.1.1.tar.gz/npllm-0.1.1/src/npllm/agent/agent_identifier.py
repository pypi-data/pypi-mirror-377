from typing import Tuple
from dataclasses import dataclass

AgentType = str
AgentId = str

@dataclass
class AgentIdentifier:
    agent_type: AgentType
    agent_id: AgentId

    def __repr__(self):
        return f"{self.agent_type}:{self.agent_id}"

    def __key(self) -> Tuple[AgentType, AgentId]:
        return (self.agent_type, self.agent_id)

    def __hash__(self) -> int:
        return hash(self.__key())