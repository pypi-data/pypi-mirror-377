import inspect
import threading
import asyncio

from allm.llms.llm import LLM
from allm.utils.message_bus import Message, MessageBus
from allm.utils.agent_identifier import AgentIdentifier
import allm.utils.models as models


class BaseAgent(LLM):
    next_agent_id = 0
    lock = threading.Lock()

    def get_next_agent_id(self) -> str:
        with self.lock:
            agent_id = BaseAgent.next_agent_id
            BaseAgent.next_agent_id += 1

        return f"{agent_id:04d}"

    def __init__(self, role: str="", model: str=models.GEMINI_2_5_FLASH, 
                 agent_identifier: AgentIdentifier=None, message_bus: MessageBus=None):
        LLM.__init__(self, role=role, model=model)

        if agent_identifier is None:
            agent_type = self.__class__.__name__
            agent_id = self.get_next_agent_id()
            self.agent_identifier = AgentIdentifier(agent_type=agent_type, agent_id=agent_id)
        else:
            self.agent_identifier = agent_identifier
        
        self.message_bus = message_bus
        if self.message_bus:
            self.register_message_handlers()

    def register_message_handlers(self):
        for _, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, '_message_handler_types'):
                message_types = getattr(method, '_message_handler_types')
                for msg_type in message_types:
                    self.message_bus.register_handler(
                        agent_identifier=self.agent_identifier,
                        message_type=msg_type,
                        handler=method
                    )

    def send_message(self, to: AgentIdentifier, message: Message) -> None:
        if self.message_bus:
            self.message_bus.send_message(to, message)
        else:
            raise RuntimeError("Message bus is not set for this agent")