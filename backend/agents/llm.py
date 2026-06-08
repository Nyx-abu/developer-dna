import os
import logging
from typing import Any

from django.conf import settings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings

logger = logging.getLogger(__name__)

def get_llm() -> BaseChatModel | Any:
    """Returns Gemini or LlamaCpp fallback based on configuration."""
    if settings.GEMINI_API_KEY:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                temperature=settings.GEMINI_TEMPERATURE
            )
        except ImportError:
            logger.error("langchain-google-genai is not installed.")
            raise
    else:
        try:
            from langchain_community.llms import LlamaCpp
            if not os.path.exists(settings.QWEN3_MODEL_PATH):
                raise FileNotFoundError(f"Offline model not found at {settings.QWEN3_MODEL_PATH}")
            logger.info("Loading Qwen3 fallback model...")
            return LlamaCpp(
                model_path=settings.QWEN3_MODEL_PATH,
                n_ctx=4096,
                temperature=settings.GEMINI_TEMPERATURE
            )
        except ImportError:
            logger.error("llama-cpp-python is not installed.")
            raise

def get_embeddings() -> Embeddings | Any:
    """Returns embeddings model."""
    if settings.GEMINI_API_KEY:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
            return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        except ImportError:
            logger.error("langchain-google-genai is not installed.")
            raise
    else:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        except ImportError:
            logger.error("sentence-transformers is not installed.")
            raise
