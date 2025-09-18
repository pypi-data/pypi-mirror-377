# Sunwaee

The almost-everything package.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![Tests](https://img.shields.io/badge/tests-98%20passed-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](tests/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📦 Installation

```bash
# basic
pip install sunwaee

# dev
pip install sunwaee[dev]
```

### æ-gen

All LLMs, one response format. Includes usage, cost and performance metrics like reasoning duration and throughput.

> ægen doesn't use provider-specific libraries (e.g. openai, anthropic, google...) and parses the raw HTTP responses (including server-sent event streams) directly, meaning there is only 1 dependency: aiohttp.

#### 📊 Response Format

```python
{
    "model": {
        "name": "gpt-5", # str
        "display_name": "GPT 5" # str
    },
    "provider": {
        "name": "openai", # str
        "url": "https://api.openai.com/v1/chat/completions" # str
    },
    "reasoning": "Model's internal reasoning (when available)", # str
    "content": "The main response content", # str
    "tool_calls": [
        {
            "id": "call_123",
            "name": "function_name",
            "arguments": {"param": "value"}
        }
    ], # list[dict[id: str, name: str, arguments:dict]]
    "raw": "Complete raw response from the model", # str
    "error": {
        "error_status": 0, # int
        "error_message": None # str
    },
    "usage": {
        "prompt_tokens": 150, # int
        "completion_tokens": 200, # int
        "total_tokens": 350 # int
    },
    "cost": {
        "prompt_cost": 0.00045, # float
        "completion_cost": 0.003, # float
        "total_cost": 0.00345, # float
    },
    "performance": {
        "latency": 1.2, # float
        "reasoning_duration": 0.4, # float
        "content_duration": 0.8, # float
        "total_duration": 1.2, # float
        "throughput": 166, # int
    },
    "streaming": False, # bool
}
```

#### Usage

```python
import asyncio
from sunwaee.aegen import async_completion

tools = [
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
]

async def main():
    messages = [
        {"role": "system": "content": "You are a helpful assistant."},
        {"role": "user", "content": "What's the latest news about AI?"}
    ]

    # NOTE we use `async for` for both the regular and streaming completion
    # regular: one block
    # streaming: multiple blocks with cumulative content/reasoning/tool_calls
    # usage, cost and performance will be in the last block in streaming mode
    async for block in async_completion(
        "openai/gpt-5",
        messages=messages,
        tools=tools,
        streaming=False
    ):
        if block["reasoning"]:
            print(f"🤔 Reasoning: {block['reasoning']}")
        if block["content"]:
            print(f"💬 Content: {block['content']}")
        if block["tool_calls"]:
            print(f"🔧 Tool calls: {len(block['tool_calls'])}")

asyncio.run(main())
```
