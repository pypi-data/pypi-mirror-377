<div align="center">
<h1>🚀 LLM Hippocampus</h1>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Language](https://img.shields.io/github/languages/top/redis-developer/redis-rag-workbench)
![GitHub last commit](https://img.shields.io/github/last-commit/redis-developer/redis-rag-workbench)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)

🎯 Build up and manage the LLM 's memory

</div>

🔥 **LLM Hippocampus** helping your project for building and experimenting with **Context Engineering** applications. harness the full power of Redis for **lightning-fast vector search**, **intelligent semantic caching**, **persistent LLM memory**, and **smart context engineering **.

✨ **What makes this special?**
- 🚀 **One-command setup** - pip install llm-hippocampus
- ⚡  **LLM support** - OpenAI
- 🎯 **Redis-powered** - Vector search, caching, and memory management
- 🐳 **Docker ready** - Building... 
- 🔧 **Developer-first** - Support to Hot load by installing llm-hippocampus

---

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Available Commands](#available-commands)
  - [Development Workflows](#development-workflows)
  - [Environment Configuration](#environment-configuration)
- [Using Google VertexAI](#using-google-vertexai)
- [Project Structure](#project-structure)
- [Connecting to Redis Cloud](#connecting-to-redis-cloud)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Learn More](#learn-more)


## Quick Start

**Get up and install in your project:**

```bash
pip install llm-hippocampus
or
uv add llm-hippocampus
```

Welcome to LLM Hippocampus! 🎉

---

## Prerequisites

1. Make sure you have the following tools available:
   - [python](https://www.docker.com/products/docker-desktop/) 3.11+
   - [uv](https://docs.astral.sh/uv/)
   - [Redis Stack](https://redis.io/)
2. Setup one or more of the following:
   - [OpenAI API](https://platform.openai.com/)
     - You will need an API Key

## Getting Started
```python
from dotenv import load_dotenv
from llm_hippocampus import env
from llm_hippocampus.core.utils import list2np_array
from llm_hippocampus.core.redis import create_search_index, client, load_data2search_index, vector_query
from llm_hippocampus.session import Session
load_dotenv()
# Load the model
session = Session()
embeddings = session.get_embedding_model()
schema = {
    "index": {
        "name": "data_agent_chain",
        "prefix": "data_agent_chain",
    },
    "fields": [
        {"name": "query", "type": "text"},
        {"name": "scope", "type": "text"},
        {"name": "intent", "type": "text"},
        {
            "name": "query_embedding",
            "type": "vector",
            "attrs": {
                "dims": 768,
                "distance_metric": "cosine",
                "algorithm": "flat",
                "datatype": "float32"
            }
        }
    ]
}

data = [
    {
        'query': 'SAAJ91的管理费率和托管费率是多少？',
        'scope': "产品基本信息",
        'intent': '管理费率、托管费率',
        'query_embedding': list2np_array(embeddings.encode(
            "SAAJ91的管理费率和托管费率是多少？",
            precision=schema["fields"][3]["attrs"]["datatype"],
            truncate_dim=schema["fields"][3]["attrs"]["dims"])).tobytes()
    },
    {
        'query': 'SATP77在于2025年06月01日至2025年06月30日的股票持仓明细',
        'scope': "股票持仓信息",
        'intent': '股票持仓信息',
        'query_embedding': list2np_array(embeddings.encode(
            "SATP77在于2025年06月01日至2025年06月30日的股票持仓明细",
            precision=schema["fields"][3]["attrs"]["datatype"],
            truncate_dim=schema["fields"][3]["attrs"]["dims"])).tobytes()
    },
    {
        'query': '截至于2025年01月01日至2025年12月31日，001120的户均定投金额？',
        'scope': "客户定投情况",
        'intent': '客户定投情况',
        'query_embedding': list2np_array(embeddings.encode(
            "截至于2025年01月01日至2025年12月31日，001120的户均定投金额",
            precision=schema["fields"][3]["attrs"]["datatype"],
            truncate_dim=schema["fields"][3]["attrs"]["dims"])).tobytes()
    }
]

redis_client = client(env.REDIS_URL)
index = create_search_index(redis_client, schema)
keys = load_data2search_index(index, data)

query = "400001的管理费率"
args = {
    "distance_threshold": session.distance_threshold,
    "top_k": session.top_k,
    "vector_field_name": "query_embedding",
    "precision": schema["fields"][3]["attrs"]["datatype"],
    "truncate_dim": schema["fields"][3]["attrs"]["dims"],
    "return_fileds": ["query", "scope", "intent"],
}

results = vector_query(query, index, embeddings, schema, **args)
```

### Development Workflows
- Building


## Project Structure


## Contributing

🤝 Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Troubleshooting

## Learn More
