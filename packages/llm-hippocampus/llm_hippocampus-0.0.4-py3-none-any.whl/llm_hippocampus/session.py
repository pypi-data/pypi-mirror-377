# -*- coding: utf-8 -*-
import os.path
from typing import List

from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import (
    OpenAIEmbeddings,
)
from langchain_core.messages.chat import ChatMessage
from redisvl.utils.rerank import HFCrossEncoderReranker
from redisvl.utils.utils import create_ulid
from sentence_transformers import SentenceTransformer

from .core.cached_llm import CachedLLM
from .core.logger import logger
from . import env
from .core import memory

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class Session:
    def __init__(self, llm = None, session_id = None, embedding = None, rerankers = None) -> None:
        missing_vars = []
        self.session_id = create_ulid() if session_id is None else session_id
        self.redis_url = env.REDIS_URL
        self.openai_api_key = env.OPENAI_API_KEY
        self.initialized = False
        self.RERANKERS = {}
        if rerankers and env.USE_RERANKERS:
            self.RERANKERS = rerankers

        # Initialize non-API dependent variables
        self.chunk_size = env.CHUNK_SIZE
        self.chunking_technique = env.CHUNKING_TECHNIQUE
        self.N = 0
        self.count = 0
        self.use_semantic_cache = env.USE_SEMANTIC_CACHE
        self.use_rerankers = env.USE_RERANKERS
        self.top_k = env.TOP_K
        self.distance_threshold = env.DISTANCE_THRESHOLD
        self.use_chat_history = env.USE_CHAT_HISTORY
        self.reranker_type = env.RERANKER_TYPE
        logger.info("Initializing LLM")
        if llm is not None:
            self.llm = llm.get('llm')
            self.llm_provider = llm.get('provider')

        if llm is not None and (not self.llm or not self.llm_provider):
            missing_vars.append(llm)

        self.cached_llm = None
        self.vector_store = None
        self.llmcache = None
        self.index_name = None
        self.memory = memory.Memory(self.redis_url, self.session_id)
        if embedding:
            self.embedding_model_provider = embedding['provider']
            self.embedding = embedding['embedding']
        else:
            self.embedding = self.get_embedding_model()
            self.embedding_model_provider = env.EMBEDDING_MODEL_PROVIDER

        if missing_vars:
            raise ValueError(f"模型初始化记忆发生异常，未设置必要的环境变量或传入的{missing_vars}不正确")

    def initialize(self):
        # Initialize rerankers
        if self.use_rerankers:
            logger.info("Initializing rerankers")

            self.RERANKERS = {
                "HuggingFace": HFCrossEncoderReranker(env.RERANKER_MODEL),
            }
            logger.info("Rerankers initialized")

        # Init chat history if use_chat_history is True
        if self.use_chat_history:
            self.memory.init_chat_history(self.session_id)
            self.memory.get_chat_history(self.session_id)
        else:
            logger.info("未开启对话历史")

    def close(self):
        self.memory.clear_short_term_memory()

    def get_embedding_model(self):
        """Get the right embedding model based on settings and config"""
        print(
            f"Embeddings for provider: {env.EMBEDDING_MODEL_PROVIDER} and model: {env.EMBEDDING_MODEL}"
        )
        match env.EMBEDDING_MODEL_PROVIDER.lower():
            case "openai":
                return OpenAIEmbeddings(model=env.EMBEDDING_MODEL)
            case "sentence-transformer":
                return SentenceTransformer(env.EMBEDDING_MODEL)

        return None

    def update_top_k(self, new_top_k: int):
        self.top_k = new_top_k

    def update_distance_threshold(self, new_threshold: float):
        self.distance_threshold = new_threshold

    def get_last_cache_status(self) -> bool:
        if isinstance(self.cached_llm, CachedLLM):
            return self.cached_llm.get_last_cache_status()
        return False

    def rerank_results(self, query, results):
        if not self.use_rerankers:
            return results, None, None

        reranker = self.RERANKERS[self.reranker_type]
        original_results = [r.page_content for r in results]

        reranked_results, scores = reranker.rank(query=query, docs=original_results)

        # Reconstruct the results with reranked order, using fuzzy matching
        reranked_docs = []
        for reranked in reranked_results:
            reranked_content = (
                reranked["content"] if isinstance(reranked, dict) else reranked
            )
            best_match = max(
                results, key=lambda r: self.similarity(r.page_content, reranked_content)
            )
            reranked_docs.append(best_match)

        rerank_info = {
            "original_order": original_results,
            "reranked_order": [
                r["content"] if isinstance(r, dict) else r for r in reranked_results
            ],
            "original_scores": [1.0]
            * len(results),  # Assuming original scores are not available
            "reranked_scores": scores,
        }

        return reranked_docs, rerank_info, original_results

    def rerankers(self):
        return self.RERANKERS

    def update_embedding_model_provider(self, new_provider: str):
        self.embedding_model_provider = new_provider

    ############ 历史消息 ##########
    def add_chat_history(self, history: List[HumanMessage | AIMessage | SystemMessage | ChatMessage]):
        self.memory.add_chat_history(history)

    def clear_chat_history(self):
        self.memory.clear_chat_history(self.session_id)

    def search_chat_history(self, session_id, query, size = 0):
        self.memory.search_chat_history(session_id, query, size)

    ###############################
