# standard
import json
import pytest
from unittest.mock import AsyncMock, patch

# third party
# custom
from sunwaee.aegen.agents.deepseek import DEEPSEEK_REASONER_AGENT


@pytest.fixture
def sample_deepseek_response():
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1700000000,
        "model": "deepseek-reasoner",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Based on my analysis, here's the answer.",
                    "reasoning_content": "This is my reasoning about the query.",
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "search_codebase",
                                "arguments": {"query": "authentication implementation"},
                            },
                        },
                        {
                            "id": "call_def456",
                            "type": "function",
                            "function": {
                                "name": "analyze_security",
                                "arguments": {
                                    "code_path": "/src/auth",
                                    "scan_type": "vulnerability",
                                },
                            },
                        },
                    ],
                },
                "finish_reason": "tool_calls",
            }
        ],
        "usage": {"prompt_tokens": 150, "completion_tokens": 200, "total_tokens": 350},
    }


@pytest.fixture
def sample_deepseek_stream_chunks():
    return [
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "reasoning_content": "Let me think about this",
                    },
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "delta": {"reasoning_content": " step by step."},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "Here's my response"},
                    "finish_reason": None,
                }
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "tool_calls": [
                            {
                                "id": "call_abc123",
                                "type": "function",
                                "function": {
                                    "name": "search_codebase",
                                    "arguments": '{"query": "auth"}',
                                },
                            },
                        ]
                    },
                    "finish_reason": "tool_calls",
                }
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "tool_calls": [
                            {
                                "id": "call_def456",
                                "type": "function",
                                "function": {
                                    "name": "analyze_security",
                                    "arguments": '{"code_path": "/src/auth", "scan_type": "vulnerability"}',
                                },
                            },
                        ]
                    },
                    "finish_reason": "tool_calls",
                }
            ],
        },
        {
            "id": "chatcmpl-123",
            "object": "chat.completion.chunk",
            "created": 1700000000,
            "model": "deepseek-reasoner",
            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 200,
                "total_tokens": 350,
            },
        },
    ]


class TestDeepSeekAgents:

    @pytest.mark.asyncio
    @patch.dict("os.environ", {}, clear=True)
    async def test_async_completion_missing_api_key(
        self, sample_messages_with_system_prompt
    ):
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY is not set"):
            async for _ in DEEPSEEK_REASONER_AGENT.async_completion(
                sample_messages_with_system_prompt
            ):
                break

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_non_streaming_success(
        self,
        mock_post,
        sample_deepseek_response,
        sample_messages_with_system_prompt,
        sample_tools,
    ):
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_deepseek_response)

        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        mock_post.return_value = mock_context

        blocks = []
        async for block in DEEPSEEK_REASONER_AGENT.async_completion(
            sample_messages_with_system_prompt, tools=sample_tools, streaming=False
        ):
            blocks.append(block)

        expected = {
            "model": {
                "name": DEEPSEEK_REASONER_AGENT.model.name,
                "display_name": DEEPSEEK_REASONER_AGENT.model.display_name,
                "version": DEEPSEEK_REASONER_AGENT.model.version,
            },
            "provider": {
                "name": DEEPSEEK_REASONER_AGENT.provider.name,
                "url": DEEPSEEK_REASONER_AGENT.provider.url,
            },
            "reasoning": "This is my reasoning about the query.",
            "content": "Based on my analysis, here's the answer.",
            "tool_calls": [
                {
                    "id": "call_abc123",
                    "name": "search_codebase",
                    "arguments": {"query": "authentication implementation"},
                },
                {
                    "id": "call_def456",
                    "name": "analyze_security",
                    "arguments": {
                        "code_path": "/src/auth",
                        "scan_type": "vulnerability",
                    },
                },
            ],
            "raw": """<think>This is my reasoning about the query.</think>Based on my analysis, here's the answer.<tool_call>{"id": "call_abc123", "name": "search_codebase", "arguments": {"query": "authentication implementation"}}</tool_call><tool_call>{"id": "call_def456", "name": "analyze_security", "arguments": {"code_path": "/src/auth", "scan_type": "vulnerability"}}</tool_call>""",
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
                "prompt_cost": 150 * DEEPSEEK_REASONER_AGENT.input_token_cost,
                "completion_cost": 200 * DEEPSEEK_REASONER_AGENT.output_token_cost,
                "total_cost": (
                    150 * DEEPSEEK_REASONER_AGENT.input_token_cost
                    + 200 * DEEPSEEK_REASONER_AGENT.output_token_cost
                ),
            },
            "streaming": False,
        }

        assert len(blocks) == 1

        for key, value in expected.items():
            assert blocks[0][key] == value

        assert blocks[0]["performance"]["latency"] >= 0
        assert blocks[0]["performance"]["reasoning_duration"] >= 0
        assert blocks[0]["performance"]["content_duration"] >= 0
        assert blocks[0]["performance"]["total_duration"] >= 0
        assert blocks[0]["performance"]["throughput"] >= 0

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
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
        async for block in DEEPSEEK_REASONER_AGENT.async_completion(
            sample_messages_with_system_prompt, streaming=False
        ):
            blocks.append(block)

        expected = {
            "model": {
                "name": DEEPSEEK_REASONER_AGENT.model.name,
                "display_name": DEEPSEEK_REASONER_AGENT.model.display_name,
                "version": DEEPSEEK_REASONER_AGENT.model.version,
            },
            "provider": {
                "name": DEEPSEEK_REASONER_AGENT.provider.name,
                "url": DEEPSEEK_REASONER_AGENT.provider.url,
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
    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_streaming_success(
        self,
        mock_post,
        sample_deepseek_stream_chunks,
        sample_messages_with_system_prompt,
        sample_tools,
    ):
        sse_lines = []
        for chunk in sample_deepseek_stream_chunks:
            sse_line = f"data: {json.dumps(chunk)}\n".encode("utf-8")
            sse_lines.append(sse_line)

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
        async for block in DEEPSEEK_REASONER_AGENT.async_completion(
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
                },
                "raw": None,
                "reasoning": "Let me think about this",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
                },
                "raw": None,
                "reasoning": " step by step.",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
                },
                "raw": None,
                "reasoning": None,
                "streaming": True,
                "tool_calls": [
                    {
                        "arguments": {
                            "query": "auth",
                        },
                        "id": "call_abc123",
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
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
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
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
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
                        "id": "call_def456",
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
                    "completion_cost": 0.000336,
                    "prompt_cost": 8.400000000000001e-05,
                    "total_cost": 0.00042,
                },
                "error": {
                    "error_message": None,
                    "error_status": 0,
                },
                "model": {
                    "display_name": "DeepSeek Reasoner",
                    "name": "deepseek-reasoner",
                    "version": None,
                },
                # NOTE dropped perf as throughput varies
                "provider": {
                    "name": "deepseek",
                    "url": "https://api.deepseek.com/v1/chat/completions",
                },
                "raw": "<think>Let me think about this step by step.</think>Here's my "
                'response<tool_call>{"id": "call_abc123", "name": "search_codebase", '
                '"arguments": {"query": "auth"}}</tool_call><tool_call>{"id": '
                '"call_def456", "name": "analyze_security", "arguments": {"code_path": '
                '"/src/auth", "scan_type": "vulnerability"}}</tool_call>',
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

        assert len(blocks) == 8

        # NOTE first, all but the last block
        assert blocks[:-1] == expected[:-1]

        # NOTE last block varies
        for key, value in expected[-1].items():
            assert blocks[-1][key] == value

        assert blocks[-1]["performance"]["latency"] >= 0
        assert blocks[-1]["performance"]["reasoning_duration"] >= 0
        assert blocks[-1]["performance"]["content_duration"] >= 0
        assert blocks[-1]["performance"]["total_duration"] >= 0
        assert blocks[-1]["performance"]["throughput"] >= 0

    @pytest.mark.asyncio
    @patch.dict("os.environ", {"DEEPSEEK_API_KEY": "test-key"})
    @patch("aiohttp.ClientSession.post")
    async def test_async_completion_streaming_error(
        self, mock_post, sample_messages_with_system_prompt
    ):
        error_chunk = {
            "error": {
                "type": "invalid_request_error",
                "message": "The model specified does not exist",
                "code": "model_not_found",
            }
        }

        sse_lines = [f"data: {json.dumps(error_chunk)}\n".encode("utf-8")]

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
        async for block in DEEPSEEK_REASONER_AGENT.async_completion(
            sample_messages_with_system_prompt, streaming=True
        ):
            blocks.append(block)

        # TODO
