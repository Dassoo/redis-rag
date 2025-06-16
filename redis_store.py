from dotenv import load_dotenv
from config.redis_config import RedisConnection
import os

load_dotenv()

redis_init = RedisConnection(os.getenv("REDIS_URL"))
redis_init.read_vectorstore()
