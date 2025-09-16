# -*- coding: utf-8 -*-
from typing import Dict, Optional

class ContextManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._context = {}
        return cls._instance

    def set(self, key: str, value: str) -> None:
        """添加或更新上下文键值对"""
        self._context[key] = value

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """获取上下文值"""
        return self._context.get(key, default)

    def delete(self, key: str) -> None:
        """删除上下文键值对"""
        if key in self._context:
            del self._context[key]

    def clear(self) -> None:
        """清空所有上下文数据"""
        self._context.clear()

    def get_all(self) -> Dict[str, str]:
        """获取所有上下文数据"""
        return self._context.copy()


def test():
    print()


if __name__ == '__main__':
    None
