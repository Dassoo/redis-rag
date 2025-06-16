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

# Delete book
book_to_delete = "tensorflow"
results = vectorstore.similarity_search("dummy", k=1000)
doc_ids = [doc.metadata.get("id") for doc in results if doc.metadata.get("book_id") == book_to_delete]
vectorstore.delete(ids=doc_ids)
print(f"Deleted {len(doc_ids)} documents from book '{book_to_delete}'.")