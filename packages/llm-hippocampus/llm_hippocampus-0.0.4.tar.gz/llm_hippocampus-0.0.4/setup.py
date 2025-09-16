# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name="llm-hippocampus",  # 包的名字（PyPI 上必须唯一，重名会传不上去）
    version="0.0.4",  # 版本号（格式：主版本.次版本.修订号，比如 0.0.1）
    author="joelz",
    author_email="zhongbj_26210@163.com",
    description="llm-hippocampus",
    long_description=open("README.md", encoding="utf-8").read(),  # 从 README 读取详细描述
    long_description_content_type="text/markdown",  # 说明 README 是 Markdown 格式
    url="",
    packages=find_packages(),  # 自动找到所有包
    classifiers=[  # 分类标签（帮助别人在 PyPI 上搜到你的包）
    ],
    python_requires=">=3.11",  # 支持的 Python 版本
    install_requires=[  # 你的包依赖的其他包（比如需要 requests 就写进去）
        "openai>=1.63.0",
        "python-dotenv>=1.0.0",
        "langchain>=0.3.19",
        "tiktoken>=0.9.0",
        "redis>=5.2.1",
        "langchain-community>=0.3.18",
        "langchain-huggingface>=0.1.2",
        "langchain-openai>=0.3.6",
        "langchain-experimental>=0.3.4",
        "python-ulid>=2.7.0",
        "pandas==2.2.3",
        "hf-xet>=1.1.8",
        "redisvl>=0.8.2",
        "sentence-transformers>=5.1.0",
        "langchain-redis>=0.2.3",
    ]
)

