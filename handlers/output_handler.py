from langchain_core.documents import Document
from schemas.models import EvaluationState
from config.redis_config import RedisConnection
from config.log_config import LoggingConfig

from pathlib import Path
from typing import List
import json
import os


class OutputHandler:
    def __init__(self):
        self.console = LoggingConfig().console

    def summary(self, state: EvaluationState):
        documents = state["evaluations"]
        image_id = os.path.splitext(os.path.basename(state["input_image"]))[0]
        book_label = Path(state["input_image"]).parent.name
        # Store into Redis
        for doc in documents:
            doc_text = f"Model: {doc.model}\nTranscription: {doc.transcription}\nTranslation: {doc.translation}\nKeywords: {', '.join(doc.keywords)}"
            doc_id = f"{book_label}:{image_id}"
            redis_init = RedisConnection(os.getenv("REDIS_URL"))
            vectorstore = redis_init.get_vectorstore()
            vectorstore.add_texts(
                [doc_text],
                metadatas=[{"book_id": book_label, "image_id": image_id, "id": doc_id}],
                ids=[doc_id]
            )
        # Dump to JSON
        self.save_to_json(documents, state["input_image"])
        return state

    def save_to_json(self, evals: List[Document], image_path: str):
        """Save evaluations to a JSON file"""
        if not os.path.exists(os.path.join(os.path.dirname(image_path), "json")):
            os.makedirs(os.path.join(os.path.dirname(image_path), "json"))
        fn = os.path.join(os.path.dirname(image_path), "json", os.path.splitext(os.path.basename(image_path))[0] + ".json")
        with open(fn, "w") as f:
            json.dump([e.model_dump() for e in evals], f, indent=2)

