# -*- coding: utf-8 -*-
from typing import List, Dict, Any

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages.chat import ChatMessage
from langchain_redis import RedisVectorStore, RedisChatMessageHistory
from redisvl.index import SearchIndex
from typing_extensions import override

from .logger import logger
from .. import env

class Memory:
    def __init__(self, redis_url: str, session_id: str):
        logger.info(f"[Brain]初始化记忆，Redis URL: {redis_url}")
        print("")
        self.redis_url = redis_url
        self.index: SearchIndex = None
        self.chat_history: RedisChatMessageHistory = None

    @property
    def client(self):
        """Redis client accessor."""
        return self.index.client

    def _check_vector_store_exists(self, index_name: str) -> bool:
        """Check if a vector store exists for the given index name."""
        try:
            self.client.ft(index_name).info()
            return True
        except Exception:
            return False

    def _cleanup_vector_store(self, index_name: str) -> bool:
        """Clean up the vector store index and its documents."""
        if not self._check_vector_store_exists(index_name):
            return True

        try:
            self.client.ft(index_name).dropindex(delete_documents=True)
            logger.info(f"Successfully cleaned up vector store: {index_name}")
            return True
        except Exception as e:
            logger.warning(f"Could not clean up vector store {index_name}: {e}")
            return False

    def init_chat_history(self, session_id: str):

        try:
            self.chat_history = RedisChatMessageHistory(
                session_id=session_id,
                redis_url=self.redis_url,
                index_name="chat_history",
                ttl=env.CLIENT_ACTIVE_TIME,
            )
            logger.info(
                f"[Brain]初始化历史消息窗口成功，会话ID: {session_id}，Redis URL: {self.redis_url}")

        except Exception as e:
            logger.warning(
                f"[Brain]初始化历史消息窗口失败，会话ID: {session_id}，Redis URL: {self.redis_url}，错误信息: {e}")

    def add_chat_history(
        self, history: List[HumanMessage | AIMessage | SystemMessage | ChatMessage]
    ):
        if self.chat_history is not None:
            for msg in history:
                self.chat_history.add_message(msg)
            return f"[Brain]添加消息历史成功，[window:chat_history]总数：{len(self.chat_history.messages)}，新增数：{len(history)}."
        return "[Brain]添加消息历史失败."

    def get_chat_history(self, session_id, size: int = env.CHAT_HISTORY_WINDOW_SIZE):
        if self.chat_history is None or self.chat_history.session_id != session_id:
            self.init_chat_history(session_id)

        messages = self.chat_history.messages
        if size > 0:
            messages = messages[-size:]
        else:
            size = len(messages)

        logger.debug(
            f"[Brain]加载消息历史成功，[window:chat_history]总数：{len(self.chat_history.messages)}，获取数：{size}.")

        formatted_history = []
        for msg in messages:
            if msg.type == "human":
                formatted_history.append(f"👤 **Human**: {msg.content}\n")
            elif msg.type == "ai":
                formatted_history.append(f"🤖 **AI**: {msg.content}\n")
        return "\n".join(formatted_history)

    def search_chat_history(self, session_id, query
                            , size: int = env.CHAT_HISTORY_WINDOW_SIZE) \
            -> List[Dict[str, Any]]:

        if not self.chat_history:
            return []

        try:
            if size > 0:
                messages = self.chat_history.search_messages(query, size)
            else:
                messages = self.chat_history.search_messages(query)
                size = len(messages)
        except Exception as e:
            logger.warning(f"[Brain]搜索消息历史失败，会话ID: {session_id}，查询: {query}，错误信息: {e}")
            return []

        logger.debug(
            f"[Brain]搜索消息历史成功，会话ID: {session_id}，查询: {query}，[window:chat_history]总数：{len(self.chat_history.messages)}，获取数：{size}.")

        return messages

    def clear_chat_history(self, session_id):
        if not self.chat_history:
            return "[Brain]当前会话无历史消息"
        self.chat_history.clear()
        return "[Brain]消息历史已清空"

    def clear_short_term_memory(self):
        if self.chat_history:
            try:
                self.chat_history.clear()
            except Exception as e:
                logger.debug(f"清理会话历史异常: {str(e)}")

if __name__ == '__main__':
    None
