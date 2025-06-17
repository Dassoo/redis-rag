from langchain_redis import RedisConfig, RedisVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from config.log_config import LoggingConfig
from rich.prompt import Prompt
from rich.panel import Panel
from collections import defaultdict
from dotenv import load_dotenv
import os


class RedisConnection:
    """Class for initializing Redis connection and vector store."""

    def __init__(self, url):
        """Initialize Redis connection and vector store."""
        load_dotenv()
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
        self.config = RedisConfig(
            index_name="index",
            redis_url=os.getenv("REDIS_URL", f"{url}"),
            metadata_schema=[
                {"name": "book_id", "type": "tag"},
                {"name": "image_id", "type": "tag"},
            ],
        )

        self.vectorstore = RedisVectorStore(self.embeddings, config=self.config)

    def get_vectorstore(self) -> RedisVectorStore:
        """Return the initialized vector store."""
        return self.vectorstore
    
    def get_config(self) -> RedisConfig:
        """Return the initialized config."""
        return self.config
        
    def read_vectorstore(self) -> None:
        """Fetch and display documents from the RedisVectorStore."""
        console = LoggingConfig().console
        console.print("Fetching all available documents from the RedisVectorStore...", style="system")
        docs = self.vectorstore.similarity_search("dummy", k=1000)
        books = defaultdict(lambda: defaultdict(list))
        for doc in docs:
            book = doc.metadata.get("book_id", "unknown")
            image_id = doc.metadata.get("image_id", "unknown")
            books[book][image_id].append(doc)

        book_names = sorted(books.keys())

        console.print("\n📚 [info]Available books:[/info]")
        for i, book in enumerate(book_names):
            console.print(f"[info]{i}[/info]: {book}")

        try:
            book_index = int(Prompt.ask("\nSelect a book number to view", console=console))
            selected_book = book_names[book_index]
        except (ValueError, IndexError):
            console.print("❌ Invalid book selection.", style="error")
            exit()

        # Select document in book
        image_ids = sorted(books[selected_book].keys())

        console.print(f"\n📦 [info]Documents in book '{selected_book}':[/info]")
        for i, img_id in enumerate(image_ids):
            console.print(f"[info]{i}[/info]: {img_id}")

        try:
            index = int(Prompt.ask("\nSelect a page number to view", console=console))
            selected_id = image_ids[index]
        except (ValueError, IndexError):
            console.print("❌ Invalid page selection.", style="error")
            exit()

        # Display document
        console.print(f"\n📄 [document]Content of '{selected_id}' ('{selected_book}'):[/document]")

        for doc in books[selected_book][selected_id]:
            console.print(Panel.fit(
                doc.page_content.strip(),
                title=f"[bold]{selected_id}[/bold]",
                border_style="document"
            ))
