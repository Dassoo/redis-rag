import redis
from dotenv import load_dotenv
import os
from langchain_redis import RedisConfig, RedisVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

config = RedisConfig(
        index_name="index",
        redis_url=os.getenv("REDIS_URL"),
        metadata_schema=[
            {"name": "book_id", "type": "tag"},
            {"name": "image_id", "type": "tag"},
            {"name": "model", "type": "tag"},
        ],
    )

vectorstore = RedisVectorStore(embeddings, config=config)

