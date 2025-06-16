from rich.console import Console
from rich.theme import Theme
import logging

class LoggingConfig:
    """Config for logs."""
    def __init__(self):
        self.console = Console(theme=Theme({
            # Events
            "event": "bold cyan",
            "feedback": "bold yellow",
            
            # UI
            "input": "bold yellow",
            "assistant": "bold cyan",
            "system": "dim",
            "user": "bold white",
            
            # Info
            "info": "bold cyan",
            "warning": "yellow",
            "error": "bold red",
            "document": "green",
            
            # Others
            "success": "bold green",
            "primary": "bold blue",
            "secondary": "magenta",
        }))

        logging.getLogger("LiteLLM").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("asyncio").setLevel(logging.WARNING)
        logging.getLogger("redisvl").setLevel(logging.WARNING)