from dotenv import load_dotenv
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig
import os


load_dotenv()
console = LoggingConfig()

redis_init = RedisConnection(os.getenv("REDIS_URL"))
redis_init.read_vectorstore()
