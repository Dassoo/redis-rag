from functools import wraps
from config.log_config import LoggingConfig

console = LoggingConfig().console

def node(func):
    """Decorator to add logging functionality to a node."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        console.print(f"Calling node: {func.__name__}", style="system")
        result = func(*args, **kwargs)
        console.print(f"Node execution finished: {func.__name__}\n", style="system")
        return result
    return wrapper