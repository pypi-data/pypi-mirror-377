import os
import logging
from duckflow.handlers import NODE_FUNCTIONS

logger = logging.getLogger("duckflow")

class Duck:
    def __init__(self, config, defaults):
        self.id = config["id"]
        self.type = config["type"]  # e.g., "openai_chat", "duckduckgo_research", "quack_node"
        self.system_message = config.get("system_message")
        self.model = config.get("model", defaults.get("default_model"))
        self.knowledge_base = config.get("knowledge_base")
        api_key_var = defaults.get("api_key", "OPENAI_API_KEY")
        self.api_key = os.getenv(api_key_var)

    def run(self, user_input: str) -> str:
        logger.debug(f"Duck {self.id} (type={self.type}) received input: {user_input}")
        func = NODE_FUNCTIONS.get(self.type)
        if not func:
            raise ValueError(
                f"No handler registered for duck type '{self.type}' "
                f"(duck id='{self.id}'). Check your duck config or NODE_FUNCTIONS registry."
            )
        try:
            output = func(user_input, self)
            logger.info(f"Duck {self.id} (type={self.type}) produced output: {output}")
            return output
        except Exception:
            logger.exception(f"Handler for duck {self.id} (type={self.type}) failed")
            raise
