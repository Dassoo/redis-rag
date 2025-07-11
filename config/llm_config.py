from agents.extensions.models.litellm_model import LitellmModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from config.log_config import LoggingConfig

from typing import Any
from dotenv import load_dotenv
import os

load_dotenv()

class LLMConfig:
    """Centralized configuration for all LLMs in the project."""

    def __init__(self):
        self.console = LoggingConfig().console
        self._models = {}
        self._initialize_models()

    def _initialize_models(self):
        """Initialize all models"""
        # Vision model for graph analysis
        self._models['vision'] = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Query model (using LiteLLM for OpenAI Agents SDK compatibility)
        self._models['query'] = LitellmModel(
            model="gemini/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        # Embeddings model
        self._models['embeddings'] = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004"
        )

    def get_model(self, model_type: str) -> Any:
        """Get a specific model by type"""
        if model_type not in self._models:
            raise ValueError(f"Unknown model type: {model_type}")
        return self._models[model_type]

