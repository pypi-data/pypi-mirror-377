import logging
logging.basicConfig(level=logging.WARNING, format='%(name)s - %(levelname)s - %(message)s')
logging.getLogger('npllm').setLevel(logging.INFO)

from dataclasses import dataclass
from typing import List
from prompt_toolkit.shortcuts import PromptSession

from npllm.core.llm import LLM

@dataclass
class Message:
    name: str
    # Always use the same language as the user
    content: str

class ChatBot(LLM):
    def __init__(self):
        LLM.__init__(self)
        self.name = "ChatBot"
        self.prompt_session = PromptSession()
        self.session: List[Message] = []

    async def run(self):
        while True:
            user_input = await self.prompt_session.prompt_async("User: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Bye!")
                break
            self.session.append(Message(name="User", content=user_input))
            message: Message = await self.chat(self.session, self.name)
            self.session.append(message)
            print(f"{self.name}: {message.content}")

if __name__ == "__main__":
    bot = ChatBot()
    import asyncio
    asyncio.run(bot.run())