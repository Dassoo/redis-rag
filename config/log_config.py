from rich.console import Console
from rich.theme import Theme
import logging

class LoggingConfig:
    """Config for logs."""
    def __init__(self):
        self.console = Console(theme=Theme({
            "event": "bold cyan",
            "feedback": "bold yellow",
            "input": "bold yellow",
            "assistant": "bold cyan",
            "system": "dim",
            "user": "bold white",
            "info": "bold cyan",
            "warning": "yellow",
            "error": "bold red",
            "document": "green",
        }))

        logging.getLogger("LiteLLM").setLevel(logging.ERROR)
        logging.getLogger("httpx").setLevel(logging.ERROR)
        logging.getLogger("asyncio").setLevel(logging.ERROR)
        logging.getLogger("redisvl").setLevel(logging.ERROR)
