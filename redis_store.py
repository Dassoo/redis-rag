from dotenv import load_dotenv
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig
import os

load_dotenv()

redis_url = os.getenv("REDIS_URL")

console = LoggingConfig().console
console.print(f"[system]Connecting to {redis_url}[/system]")
try:
    redis_init = RedisConnection(redis_url)
    redis_init.read_vectorstore()
except Exception as e:
    console.print(f"[error]❌ Error connecting to Redis: {e}[/error]")
    exit()
