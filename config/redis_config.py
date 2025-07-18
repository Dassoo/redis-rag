from langchain_redis import RedisConfig, RedisVectorStore
from config.log_config import LoggingConfig
from config.llm_config import LLMConfig
from rich.prompt import Prompt
from rich.panel import Panel
from collections import defaultdict
from dotenv import load_dotenv
import os

class RedisConnection:
    """Class for initializing and managing Redis connection and vector store."""

    def __init__(self, url: str):
        """Initialize Redis connection and vector store."""
        load_dotenv()
        self.console = LoggingConfig().console
        self.console.print(f"Connecting to {os.getenv('REDIS_URL') or url}", style="system")

        # Get embeddings model from config
        llm_config = LLMConfig()
        self.embeddings = llm_config.get_model('embeddings')
        
        self.config = RedisConfig(
            index_name="index",
            redis_url=os.getenv("REDIS_URL", f"{url}"),
            metadata_schema=[
                {"name": "book_id", "type": "tag"},
                {"name": "image_id", "type": "tag"},
            ],
        )

        try:
            self.vectorstore = RedisVectorStore(self.embeddings, config=self.config)
        except Exception as e:
            self.console.print(f"❌ Error connecting to Redis: {e}", style="error")
            exit()

    def get_vectorstore(self) -> RedisVectorStore:
        """Return the initialized vector store."""
        return self.vectorstore
    
    def get_config(self) -> RedisConfig:
        """Return the initialized config."""
        return self.config
        
    def read_vectorstore(self) -> None:
        """Fetch and display documents from the RedisVectorStore."""
        self.console.print("Fetching all available documents from the RedisVectorStore...", style="system")
        docs = self.vectorstore.similarity_search("dummy", k=1000)
        books = defaultdict(lambda: defaultdict(list))
        for doc in docs:
            book = doc.metadata.get("book_id", "unknown")
            image_id = doc.metadata.get("image_id", "unknown")
            books[book][image_id].append(doc)

        book_names = sorted(books.keys())

        self.console.print("\n📚 [info]Available books:[/info]")
        if not book_names:
            self.console.print("No books found.", style="warning")
            return
        
        for i, book in enumerate(book_names):
            self.console.print(f"[info]{i}[/info]: {book}")

        book_index = Prompt.ask("\nSelect a book number to view (or 'quit' to exit)", console=self.console)
        if book_index.lower() == "quit" or book_index.lower() == "exit":
            return
        try:
            selected_book = book_names[int(book_index)]
        except (ValueError, IndexError):
            self.console.print("❌ Invalid book selection.", style="error")
            return

        # Select document in book
        image_ids = sorted(books[selected_book].keys())

        self.console.print(f"\n📦 [info]Documents in book '{selected_book}':[/info]")
        for i, img_id in enumerate(image_ids):
            self.console.print(f"[info]{i}[/info]: {img_id}")

        try:
            index = int(Prompt.ask("\nSelect a page number to view", console=self.console))
            selected_id = image_ids[index]
        except (ValueError, IndexError):
            self.console.print("❌ Invalid page selection.", style="error")
            exit()

        # Display document
        self.console.print(f"\n📄 [document]Content of '{selected_id}' ('{selected_book}'):[/document]")

        for doc in books[selected_book][selected_id]:
            self.console.print(Panel.fit(
                doc.page_content.strip(),
                title=f"[bold]{selected_id}[/bold]",
                border_style="document"
            ))
