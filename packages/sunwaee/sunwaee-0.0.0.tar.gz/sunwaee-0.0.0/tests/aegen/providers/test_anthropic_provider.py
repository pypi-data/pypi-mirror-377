# standard
import pytest

# third party
# custom
from sunwaee.aegen.providers.anthropic import (
    anthropic_headers_adapter,
    anthropic_tools_adapter,
    anthropic_payload_adapter,
    anthropic_sse_adapter,
    anthropic_response_adapter,
)


@pytest.fixture
def anthropic_api_key():
    return "sk-ant-test-key-12345"


@pytest.fixture
def anthropic_tools():
    return [
        {
            "name": "search_codebase",
            "description": "Search through the codebase for relevant code snippets",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant code",
                    },
                    "file_type": {
                        "type": "string",
                        "description": "Optional file extension filter (e.g., .py, .js)",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "analyze_security",
            "description": "Analyze code for security vulnerabilities",
            "input_schema": {
                "type": "object",
                "properties": {
                    "code_path": {
                        "type": "string",
                        "description": "Path to the code to analyze",
                    },
                    "scan_type": {
                        "type": "string",
                        "description": "Type of security scan to perform",
                    },
                },
                "required": ["code_path", "scan_type"],
            },
        },
    ]


class TestAnthropicProvider:

    def test_anthropic_headers_adapter_success(self, monkeypatch, anthropic_api_key):
        monkeypatch.setenv("ANTHROPIC_API_KEY", anthropic_api_key)

        headers = anthropic_headers_adapter()

        expected_headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": anthropic_api_key,
        }

        assert headers == expected_headers

    def test_anthropic_headers_adapter_missing_key(self, monkeypatch):
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is not set"):
            anthropic_headers_adapter()

    def test_anthropic_tools_adapter(self, sample_tools, anthropic_tools):
        adapted_tools = anthropic_tools_adapter(tools=sample_tools)
        assert adapted_tools == anthropic_tools

    def test_anthropic_tools_adapter_missing_tools(self):
        with pytest.raises(
            ValueError, match="Tools are required for anthropic tools adapter"
        ):
            anthropic_tools_adapter()

    def test_anthropic_payload_adapter_full(
        self,
        sample_prompt,
        sample_model,
        sample_messages,
        anthropic_tools,
    ):
        payload = anthropic_payload_adapter(
            model=sample_model,
            system_prompt=sample_prompt,
            messages=sample_messages,
            max_tokens=32000,
            tools=anthropic_tools,
        )

        expected = {
            "model": sample_model,
            "system": sample_prompt,
            "messages": sample_messages,
            "stream": False,
            "max_tokens": 32000,
            "tools": anthropic_tools,
            "thinking": {
                "type": "enabled",
                "budget_tokens": 8192,
            },
        }

        assert payload == expected

    def test_anthropic_payload_adapter_missing_model(
        self,
        sample_prompt,
        sample_messages,
    ):
        with pytest.raises(
            ValueError, match="Model is required for anthropic payload adapter"
        ):
            anthropic_payload_adapter(
                prompt=sample_prompt,
                messages=sample_messages,
                max_tokens=2048,
            )

    def test_anthropic_payload_adapter_missing_messages(
        self,
        sample_prompt,
        sample_model,
    ):
        with pytest.raises(
            ValueError, match="Messages are required for anthropic payload adapter"
        ):
            anthropic_payload_adapter(
                model=sample_model,
                prompt=sample_prompt,
                max_tokens=2048,
            )

    def test_anthropic_payload_adapter_missing_max_tokens(
        self,
        sample_model,
        sample_prompt,
        sample_messages,
    ):
        with pytest.raises(
            ValueError, match="Max tokens are required for anthropic payload adapter"
        ):
            anthropic_payload_adapter(
                model=sample_model,
                prompt=sample_prompt,
                messages=sample_messages,
            )

    def test_anthropic_sse_adapter(self):
        mapping = anthropic_sse_adapter()

        expected_mapping = {
            "content": "delta.text",
            "reasoning": "delta.thinking",
            "tool_call_id": "content_block.id",
            "tool_call_name": "content_block.name",
            "tool_call_arguments": "delta.partial_json",
            "prompt_tokens": "message.usage.input_tokens",
            "completion_tokens": "message.usage.output_tokens",
            "total_tokens": "",
        }

        assert mapping == expected_mapping

    def test_anthropic_response_adapter(self):
        mapping = anthropic_response_adapter()

        expected_mapping = {
            "content": "content.[type=text].text",
            "reasoning": "content.[type=thinking].thinking",
            "tool_call_id": "content.[type=tool_use].id",
            "tool_call_name": "content.[type=tool_use].name",
            "tool_call_arguments": "content.[type=tool_use].input",
            "prompt_tokens": "usage.input_tokens",
            "completion_tokens": "usage.output_tokens",
            "total_tokens": "",
        }

        assert mapping == expected_mapping
