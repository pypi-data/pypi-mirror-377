import queue
import threading
import logging
import asyncio
import inspect
from typing import Callable, Dict, Tuple, Type
from abc import ABC, abstractmethod

from allm.utils.agent_identifier import AgentIdentifier

logger = logging.getLogger(__name__)

class Message(ABC):
    pass


class message_handler:
    def __init__(self, *message_types: Type[Message]):
        if not message_types:
            raise RuntimeError("message_handler decorator requires at least one message type.")
        self.message_types = message_types

    def __call__(self, func: Callable):
        setattr(func, '_message_handler_types', self.message_types)
        return func


class MessageBus:
    def __init__(self, num_workers: int = 4):
        self.message_queue = queue.Queue()
        self.handler_registry: Dict[Tuple[AgentIdentifier, Type[Message]], Callable] = {}
        self.workers: list[threading.Thread] = []
        self.num_workers = num_workers
        self.is_stopped = True
        self.lock = threading.Lock()

    def register_handler(self, agent_identifier: AgentIdentifier, message_type: Type[Message], handler: Callable):
        with self.lock:
            key = (agent_identifier, message_type)
            logger.info(f"Registering handler for key: {key}")
            self.handler_registry[key] = handler

    def send_message(self, to: AgentIdentifier, message: Message):
        with self.lock:
            if self.is_stopped:
                logger.warning("Message bus is stopped. Message will not be queued.")
                return
            self.message_queue.put((to, message))

    def dispatcher_loop(self):
        while True:
            item = self.message_queue.get()
            if item is None:
                self.message_queue.task_done()
                break

            agent_id, message = item
            message_type = type(message)
            key = (agent_id, message_type)
            
            handler = self.handler_registry.get(key)
            
            if handler:
                try:
                    if inspect.iscoroutinefunction(handler):
                        asyncio.run(handler(message))
                    else:
                        handler(message)
                except Exception as e:
                    logger.error(f"Error executing handler for {key}: {e}", exc_info=True)
            else:
                # self.message_queue.put(item)
                logger.warning(f"No handler registered for key: {key}")

            self.message_queue.task_done()

    def start(self):
        with self.lock:
            if self.workers:
                logger.info("Message bus is already running.")
                return

            logger.info(f"Starting message bus with {self.num_workers} workers.")
            self.is_stopped = False
            self.workers = []
            for i in range(self.num_workers):
                worker = threading.Thread(target=self.dispatcher_loop, daemon=True)
                worker.name = f"MessageBus-Worker-{i+1}"
                worker.start()
                self.workers.append(worker)

    def is_started(self) -> bool:
        with self.lock:
            return self.workers and not self.is_stopped
        
    def is_stopped(self) -> bool:
        with self.lock:
            return not self.workers and self.is_stopped

    def stop(self):
        with self.lock:
            if not self.workers:
                logger.info("Message bus is not running.")
                return

            logger.info("Stopping message bus gracefully...")
            self.is_stopped = True

            for _ in self.workers:
                self.message_queue.put(None)
            
            workers_to_join = self.workers
            self.workers = []

        for worker in workers_to_join:
            worker.join()

        logger.info("Message bus stopped.")