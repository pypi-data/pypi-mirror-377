# -*- coding: utf-8 -*-
from dotenv import load_dotenv
from .core.utils import str_to_bool
import logging
import os
load_dotenv()
LOG_LEVEL = os.environ.get("LOG_LEVEL", logging.DEBUG)
TOP_K = int(os.environ.get("DEFAULT_TOP_K", 10))
DISTANCE_THRESHOLD = float(os.environ.get("DEFAULT_DISTANCE_THRESHOLD", 0.65))
REDIS_URL = os.environ.get("REDIS_URL",  "redis://localhost:6379")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
CHUNK_SIZE = int(os.environ.get("DEFAULT_CHUNK_SIZE", 500))
CHUNKING_TECHNIQUE = os.environ.get(
            "DEFAULT_CHUNKING_TECHNIQUE", "Recursive Character"
        )
USE_SEMANTIC_CACHE = str_to_bool(
            os.environ.get("DEFAULT_USE_SEMANTIC_CACHE")
        )
USE_RERANKERS = str_to_bool(os.environ.get("DEFAULT_USE_RERANKERS"))
RERANKER_MODEL = os.environ.get("DEFAULT_RERANKER_MODEL", "D:/model/Qwen3-Reranker-0.6B")
RERANKER_TYPE = os.environ.get("DEFAULT_RERANKER_TYPE", "HuggingFace")
USE_CHAT_HISTORY = str_to_bool(os.environ.get("DEFAULT_USE_CHAT_HISTORY"))
CHAT_HISTORY_WINDOW_SIZE = int(os.environ.get("DEFAULT_CHAT_HISTORY_WINDOW_SIZE", 10))
USE_RAGAS = str_to_bool(os.environ.get("DEFAULT_USE_RAGAS"))
EMBEDDING_MODEL_PROVIDER = os.environ.get("DEFAULT_EMBEDDING_MODEL_PROVIDER", "sentence-transformer")
EMBEDDING_MODEL = os.environ.get("DEFAULT_EMBEDDING_MODEL", "D:/model/Qwen3-Embedding-0.6B")
CLIENT_ACTIVE_TIME = int(os.environ.get("CLIENT_ACTIVE_TIME", 3600))
SHORT_TERM_MEMORY_ACTIVE_TIME = int(os.environ.get("SHORT_TERM_MEMORY_ACTIVE_TIME", 36000))
