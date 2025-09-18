# standard
# third party
import pytest

# custom
from sunwaee.aegen.provider import (
    Provider,
    default_headers_adapter,
    default_messages_adapter,
    default_tools_adapter,
    default_payload_adapter,
    default_sse_adapter,
    default_response_adapter,
)


class TestProvider:

    def test_provider_initialization(self, sample_provider_config):
        provider = Provider(
            name=sample_provider_config["name"],
            url=sample_provider_config["url"],
        )

        assert provider.name == sample_provider_config["name"]
        assert provider.url == sample_provider_config["url"]
        assert provider.headers_adapter is not None
        assert provider.messages_adapter is not None
        assert provider.tools_adapter is not None
        assert provider.payload_adapter is not None
        assert provider.sse_adapter is not None
        assert provider.response_adapter is not None

    def test_provider_custom_adapters(self, sample_provider_config):
        def custom_headers_adapter(**kwargs):
            return {"Custom": "Header"}

        provider = Provider(
            name=sample_provider_config["name"],
            url=sample_provider_config["url"],
            headers_adapter=custom_headers_adapter,
        )

        assert provider.headers_adapter == custom_headers_adapter

    def test_provider_default_headers_adapter(self, sample_api_key):
        headers = default_headers_adapter(api_key=sample_api_key)

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {sample_api_key}",
        }

        assert headers == expected_headers

    def test_provider_default_headers_adapter_missing_key(self):
        with pytest.raises(ValueError, match="API key is required"):
            default_headers_adapter()

    def test_provider_default_messages_adapter(self, sample_prompt, sample_messages):
        adapted_messages = default_messages_adapter(
            system_prompt=sample_prompt,
            messages=sample_messages,
        )

        assert adapted_messages == [
            {"role": "system", "content": sample_prompt},
            *sample_messages,
        ]
        assert len(adapted_messages) == 4
        assert adapted_messages[0]["role"] == "system"
        assert adapted_messages[1]["role"] == "user"
        assert adapted_messages[2]["role"] == "assistant"
        assert adapted_messages[3]["role"] == "tool"

    def test_provider_default_messages_adapter_missing_messages(self):
        with pytest.raises(ValueError, match="Messages are required"):
            default_messages_adapter()

    def test_provider_default_tools_adapter(self, sample_tools):
        adapted_tools = default_tools_adapter(tools=sample_tools)

        assert adapted_tools == sample_tools
        assert len(adapted_tools) == 2
        assert adapted_tools[0]["type"] == "function"
        assert adapted_tools[0]["function"]["name"] == "search_codebase"
        assert adapted_tools[1]["function"]["name"] == "analyze_security"

    def test_provider_default_tools_adapter_missing_tools(self):
        with pytest.raises(ValueError, match="Tools are required"):
            default_tools_adapter()

    def test_provider_default_payload_adapter(
        self, sample_model, sample_messages, sample_tools
    ):
        payload = default_payload_adapter(
            model=sample_model,
            messages=sample_messages,
            streaming=True,
            tools=sample_tools,
        )

        expected_payload = {
            "model": sample_model,
            "messages": sample_messages,
            "stream": True,
            "tools": sample_tools,
            "stream_options": {"include_usage": True},
        }

        assert payload == expected_payload

    def test_provider_default_payload_adapter_minimal(
        self, sample_model, sample_messages
    ):
        payload = default_payload_adapter(
            model=sample_model,
            messages=sample_messages,
        )

        expected_payload = {
            "model": sample_model,
            "messages": sample_messages,
            "stream": False,
        }

        assert payload == expected_payload

    def test_provider_default_payload_adapter_missing_model(self, sample_messages):
        with pytest.raises(ValueError, match="Model is required"):
            default_payload_adapter(messages=sample_messages)

    def test_provider_default_payload_adapter_missing_messages(self, sample_model):
        with pytest.raises(ValueError, match="Messages are required"):
            default_payload_adapter(model=sample_model)

    def test_provider_default_sse_adapter(self):
        mapping = default_sse_adapter()

        expected_mapping = {
            "content": "choices.0.delta.content",
            "reasoning": "choices.0.delta.reasoning_content",
            "tool_call_id": "choices.0.delta.tool_calls.[function].id",
            "tool_call_name": "choices.0.delta.tool_calls.[function].function.[name].name",
            "tool_call_arguments": "choices.0.delta.tool_calls.[function].function.[arguments].arguments",
            "prompt_tokens": "usage.prompt_tokens",
            "completion_tokens": "usage.completion_tokens",
            "total_tokens": "usage.total_tokens",
        }

        assert mapping == expected_mapping

    def test_provider_default_response_adapter(self):
        mapping = default_response_adapter()

        expected_mapping = {
            "content": "choices.0.message.content",
            "reasoning": "choices.0.message.reasoning_content",
            "tool_call_id": "choices.0.message.tool_calls.[function].id",
            "tool_call_name": "choices.0.message.tool_calls.[function].function.[name].name",
            "tool_call_arguments": "choices.0.message.tool_calls.[function].function.[arguments].arguments",
            "prompt_tokens": "usage.prompt_tokens",
            "completion_tokens": "usage.completion_tokens",
            "total_tokens": "usage.total_tokens",
        }

        assert mapping == expected_mapping
