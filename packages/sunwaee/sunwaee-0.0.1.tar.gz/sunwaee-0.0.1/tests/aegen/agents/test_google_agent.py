# standard
import json
import pytest
from unittest.mock import AsyncMock, patch

# third party
# custom
from sunwaee.aegen.agents.google import GEMINI_2_5_FLASH_AGENT


@pytest.fixture
def sample_google_response():
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "Based on my analysis, here's the answer.",
                        },
                        {
                            "functionCall": {
                                "name": "search_codebase",
                                "args": {"query": "authentication implementation"},
                            }
                        },
                        {
                            "functionCall": {
                                "name": "analyze_security",
                                "args": {
                                    "code_path": "/src/auth",
                                    "scan_type": "vulnerability",
                                },
                            }
                        },
                    ],
                    "role": "model",
                },
                "finishReason": "STOP",
                "index": 0,
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 150,
            "candidatesTokenCount": 200,
            "totalTokenCount": 350,
        },
        "modelVersion": "gemini-2.5-flash",
    }


@pytest.fixture
def sample_google_stream_chunks():
    # NOTE no reasoning access for google models
    return [
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": "Here's my response",
                            }
                        ],
                        "role": "model",
                    },
                    "index": 0,
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "functionCall": {
                                    "name": "search_codebase",
                                    "args": {
                                        "query": "authentication implementation",
                                    },
                                }
                            }
                        ],
                        "role": "model",
                    },
                    "index": 0,
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "functionCall": {
                                    "name": "analyze_security",
                                    "args": {
                                        "code_path": "/src/auth",
                                        "scan_type": "vulnerability",
                                    },
                                }
                            }
                        ],
                        "role": "model",
                    },
                    "finishReason": "STOP",
                    "index": 0,
                }
            ]
        },
        {
            "candidates": [
                {
                    "content": {"parts": [], "role": "model"},
                    "finishReason": "STOP",
                    "index": 0,
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 150,
                "candidatesTokenCount": 200,
                "totalTokenCount": 350,
            },
        },
    ]


class TestGoogleAgents:

    @pytest.mark.asyncio
    @patch.dict("os.environ", {}, clear=True)
    async def test_async_completion_missing_api_key(
        self, sample_messages_with_system_prompt
    ):
        with pytest.raises(ValueError, match="GOOGLE_API_KEY is not set"):
            async for _ in GEMINI_2_5_FLASH_AGENT.async_completion(
                sample_messages_with_system_prompt
            ):
                break

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_non_streaming_success(
        self,
        mock_post,
        sample_google_response,
        sample_messages_with_system_prompt,
        sample_tools,
    ):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_google_response)

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_post.return_value = mock_context

        blocks = []
        async for block in GEMINI_2_5_FLASH_AGENT.async_completion(
            sample_messages_with_system_prompt, tools=sample_tools, streaming=False
        ):
            blocks.append(block)

        expected = {
            "model": {
                "name": GEMINI_2_5_FLASH_AGENT.model.name,
                "display_name": GEMINI_2_5_FLASH_AGENT.model.display_name,
                "version": GEMINI_2_5_FLASH_AGENT.model.version,
            },
            "provider": {
                "name": GEMINI_2_5_FLASH_AGENT.provider.name,
                "url": GEMINI_2_5_FLASH_AGENT.provider.url,
            },
            "reasoning": None,
            "content": "Based on my analysis, here's the answer.",
            "error": {
                "error_status": 0,
                "error_message": None,
            },
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 200,
                "total_tokens": 350,
            },
            "cost": {
                "prompt_cost": 150 * GEMINI_2_5_FLASH_AGENT.input_token_cost,
                "completion_cost": 200 * GEMINI_2_5_FLASH_AGENT.output_token_cost,
                "total_cost": (
                    150 * GEMINI_2_5_FLASH_AGENT.input_token_cost
                    + 200 * GEMINI_2_5_FLASH_AGENT.output_token_cost
                ),
            },
            "streaming": False,
        }

        assert len(blocks) == 1

        for key, value in expected.items():
            assert blocks[0][key] == value

        assert blocks[0]["raw"].startswith(
            "Based on my analysis, here's the answer.<tool_call>"
        )

        # NOTE ids are generated at random so assert line by line
        assert isinstance(blocks[0]["tool_calls"][0]["id"], str)
        assert blocks[0]["tool_calls"][0]["name"] == "search_codebase"
        assert blocks[0]["tool_calls"][0]["arguments"] == {
            "query": "authentication implementation"
        }

        assert isinstance(blocks[0]["tool_calls"][1]["id"], str)
        assert blocks[0]["tool_calls"][1]["name"] == "analyze_security"
        assert blocks[0]["tool_calls"][1]["arguments"] == {
            "code_path": "/src/auth",
            "scan_type": "vulnerability",
        }

        assert blocks[0]["performance"]["latency"] >= 0
        assert blocks[0]["performance"]["reasoning_duration"] >= 0
        assert blocks[0]["performance"]["content_duration"] >= 0
        assert blocks[0]["performance"]["total_duration"] >= 0
        assert blocks[0]["performance"]["throughput"] >= 0

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_non_streaming_error(
        self, mock_post, sample_messages_with_system_prompt
    ):
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text = AsyncMock(return_value="Bad Request: Invalid model")

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_post.return_value = mock_context

        blocks = []
        async for block in GEMINI_2_5_FLASH_AGENT.async_completion(
            sample_messages_with_system_prompt, streaming=False
        ):
            blocks.append(block)

        expected = {
            "model": {
                "name": GEMINI_2_5_FLASH_AGENT.model.name,
                "display_name": GEMINI_2_5_FLASH_AGENT.model.display_name,
                "version": GEMINI_2_5_FLASH_AGENT.model.version,
            },
            "provider": {
                "name": GEMINI_2_5_FLASH_AGENT.provider.name,
                "url": GEMINI_2_5_FLASH_AGENT.provider.url,
            },
            "reasoning": None,
            "content": None,
            "tool_calls": [],
            "raw": None,
            "error": {
                "error_status": 400,
                "error_message": "Bad Request: Invalid model",
            },
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "cost": {
                "prompt_cost": 0,
                "completion_cost": 0,
                "total_cost": 0,
            },
            "streaming": False,
        }

        assert len(blocks) == 1

        for key, value in expected.items():
            assert blocks[0][key] == value

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_streaming_success(
        self,
        mock_post,
        sample_google_stream_chunks,
        sample_messages_with_system_prompt,
        sample_tools,
    ):
        sse_lines = []
        for chunk in sample_google_stream_chunks:
            chunk_as_splitted_str = json.dumps(chunk, indent=2).split("\n")
            for sc in chunk_as_splitted_str:
                sse_lines.append(sc.encode("utf-8"))
            sse_lines.append(",\n".encode("utf-8"))
        sse_lines.append("]".encode("utf-8"))
        sse_lines[0] = "[{\n".encode("utf-8")

        class MockContent:
            def __init__(self, lines):
                self.lines = lines
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index >= len(self.lines):
                    raise StopAsyncIteration
                line = self.lines[self.index]
                self.index += 1
                return line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = MockContent(sse_lines)

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_post.return_value = mock_context

        blocks = []
        async for block in GEMINI_2_5_FLASH_AGENT.async_completion(
            sample_messages_with_system_prompt, tools=sample_tools, streaming=True
        ):
            blocks.append(block)

        expected = [
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": "Reasoning tokens are not available for `Gemini 2.5 Flash`...",
                "streaming": True,
                "tool_calls": [],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": "Here's my response",
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [
                    {
                        "arguments": {
                            "query": "authentication implementation",
                        },
                        "id": "tc_77e86825-d06c-43b7-8d07-836b32fba544",
                        "name": "search_codebase",
                    },
                ],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0,
                    "prompt_cost": 0.0,
                    "total_cost": 0.0,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                "performance": {
                    "content_duration": 0.0,
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "throughput": 0,
                    "total_duration": 0.0,
                },
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [
                    {
                        "arguments": {
                            "code_path": "/src/auth",
                            "scan_type": "vulnerability",
                        },
                        "id": "tc_2e27fde3-ebb5-446f-b23e-ba68847e72bd",
                        "name": "analyze_security",
                    },
                ],
                "usage": {
                    "completion_tokens": 0,
                    "prompt_tokens": 0,
                    "total_tokens": 0,
                },
            },
            {
                "content": None,
                "cost": {
                    "completion_cost": 0.0005,
                    "prompt_cost": 4.4999999999999996e-05,
                    "total_cost": 0.000545,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "Gemini 2.5 Flash",
                    "name": "gemini-2.5-flash",
                    "version": None,
                },
                # NOTE dropped perf as it varies
                "provider": {
                    "name": "google",
                    "url": "https://generativelanguage.googleapis.com/v1beta/models/<|model_name|>:<|gen_method|>",
                },
                # NOTE dropped raw as tc id varies
                "reasoning": None,
                "streaming": True,
                "tool_calls": [],
                "usage": {
                    "completion_tokens": 200,
                    "prompt_tokens": 150,
                    "total_tokens": 350,
                },
            },
        ]

        assert len(blocks) == 7
        # NOTE first, all but the last 3 blocks
        assert blocks[:-3] == expected[:-3]

        # NOTE last block varies
        for key, value in expected[-1].items():
            assert blocks[-1][key] == value

        assert blocks[-1]["raw"].startswith("Here's my response<tool_call>")

        # NOTE ids are generated at random so assert line by line
        assert isinstance(blocks[-3]["tool_calls"][0]["id"], str)
        assert blocks[-3]["tool_calls"][0]["name"] == "search_codebase"
        assert blocks[-3]["tool_calls"][0]["arguments"] == {
            "query": "authentication implementation"
        }

        assert isinstance(blocks[-2]["tool_calls"][0]["id"], str)
        assert blocks[-2]["tool_calls"][0]["name"] == "analyze_security"
        assert blocks[-2]["tool_calls"][0]["arguments"] == {
            "code_path": "/src/auth",
            "scan_type": "vulnerability",
        }

        assert blocks[-1]["performance"]["latency"] >= 0
        assert blocks[-1]["performance"]["reasoning_duration"] >= 0
        assert blocks[-1]["performance"]["content_duration"] >= 0
        assert blocks[-1]["performance"]["total_duration"] >= 0
        assert blocks[-1]["performance"]["throughput"] >= 0

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_streaming_error(
        self, mock_post, sample_messages_with_system_prompt
    ):
        error_chunk = {
            "error": {
                "code": 429,
                "message": "Quota exceeded for requests per minute per model",
                "status": "RESOURCE_EXHAUSTED",
            }
        }

        sse_lines = []
        sse_lines.append("[{\n".encode("utf-8"))
        chunk_json = json.dumps(error_chunk, indent=2)
        sse_lines.append(chunk_json.encode("utf-8"))
        sse_lines.append("\n]\n".encode("utf-8"))

        class MockContent:
            def __init__(self, lines):
                self.lines = lines
                self.index = 0

            def __aiter__(self):
                return self

            async def __anext__(self):
                if self.index >= len(self.lines):
                    raise StopAsyncIteration
                line = self.lines[self.index]
                self.index += 1
                return line

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.content = MockContent(sse_lines)

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_post.return_value = mock_context

        blocks = []
        async for block in GEMINI_2_5_FLASH_AGENT.async_completion(
            sample_messages_with_system_prompt, streaming=True
        ):
            blocks.append(block)

        # TODO
