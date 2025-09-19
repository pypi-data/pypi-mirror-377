# standard
# third party
import pytest

# custom
from sunwaee.aegen import Agent
from sunwaee.aegen import Model
from sunwaee.aegen import Provider


@pytest.fixture
def sample_model():
    """Sample model for testing."""
    return Model(name="gpt-4", display_name="GPT-4", origin="openai", version="0613")


@pytest.fixture
def sample_provider():
    """Sample provider for testing."""
    return Provider(
        name="test_provider", url="https://api.test.com/v1/chat/completions"
    )


@pytest.fixture
def sample_agent(sample_model, sample_provider):
    """Sample agent for testing."""
    return Agent(
        name="test_agent",
        model=sample_model,
        provider=sample_provider,
        max_input_tokens=8192,
        max_output_tokens=4096,
        cost_per_1m_input_tokens=10.0,
        cost_per_1m_output_tokens=30.0,
        supports_tools=True,
        supports_reasoning=True,
        reasoning_tokens_access=True,
    )


class TestAgent:

    def test_agent_initialization(self, sample_model, sample_provider):
        """Test Agent initialization with all parameters."""
        agent = Agent(
            name="test_agent",
            model=sample_model,
            provider=sample_provider,
            max_input_tokens=8192,
            max_output_tokens=4096,
            cost_per_1m_input_tokens=10.0,
            cost_per_1m_output_tokens=30.0,
            supports_tools=True,
            supports_reasoning=True,
            reasoning_tokens_access=True,
        )

        assert agent.name == "test_agent"
        assert agent.model == sample_model
        assert agent.provider == sample_provider
        assert agent.max_input_tokens == 8192
        assert agent.max_output_tokens == 4096
        assert agent.cost_per_1m_input_tokens == 10.0
        assert agent.cost_per_1m_output_tokens == 30.0
        assert agent.supports_tools is True
        assert agent.supports_reasoning is True
        assert agent.reasoning_tokens_access is True

        # Test computed properties
        assert agent.input_token_cost == 10.0 / 1_000_000
        assert agent.output_token_cost == 30.0 / 1_000_000

    def test_agent_initialization_defaults(self, sample_model, sample_provider):
        """Test Agent initialization with default values."""
        agent = Agent(
            name="test_agent",
            model=sample_model,
            provider=sample_provider,
            max_input_tokens=4096,
            max_output_tokens=2048,
            cost_per_1m_input_tokens=5.0,
            cost_per_1m_output_tokens=15.0,
        )

        assert agent.supports_tools is False
        assert agent.supports_reasoning is False
        assert agent.reasoning_tokens_access is False

    def test_agent_block_method_minimal(self, sample_agent):
        """Test _block method with minimal parameters."""
        block = sample_agent._block()

        expected_keys = [
            "model",
            "provider",
            "reasoning",
            "content",
            "tool_calls",
            "raw",
            "error",
            "usage",
            "cost",
            "performance",
            "streaming",
        ]

        for key in expected_keys:
            assert key in block

        # Check model info
        assert block["model"]["name"] == "gpt-4"
        assert block["model"]["display_name"] == "GPT-4"
        assert block["model"]["version"] == "0613"

        # Check provider info
        assert block["provider"]["name"] == "test_provider"
        assert block["provider"]["url"] == "https://api.test.com/v1/chat/completions"

        # Check defaults
        assert block["reasoning"] is None
        assert block["content"] is None
        assert block["tool_calls"] == []
        assert block["raw"] is None
        assert block["streaming"] is False

        # Check error defaults
        assert block["error"]["error_status"] == 0
        assert block["error"]["error_message"] is None

        # Check usage defaults
        assert block["usage"]["prompt_tokens"] == 0
        assert block["usage"]["completion_tokens"] == 0
        assert block["usage"]["total_tokens"] == 0

        # Check cost calculations
        assert block["cost"]["prompt_cost"] == 0.0
        assert block["cost"]["completion_cost"] == 0.0
        assert block["cost"]["total_cost"] == 0.0

        # Check performance defaults
        assert block["performance"]["latency"] == 0.0
        assert block["performance"]["reasoning_duration"] == 0.0
        assert block["performance"]["content_duration"] == 0.0
        assert block["performance"]["total_duration"] == 0.0
        assert block["performance"]["throughput"] == 0

    def test_agent_block_method_full(self, sample_agent):
        """Test _block method with all parameters."""
        tool_calls = [
            {"id": "call_123", "name": "test_tool", "arguments": {"arg": "value"}}
        ]

        block = sample_agent._block(
            reasoning="Test reasoning",
            content="Test content",
            tool_calls=tool_calls,
            raw="<think>Test reasoning</think>Test content<tool_call>tc</tool_call>",
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            latency=2.5,
            reasoning_duration=1.0,
            content_duration=1.2,
            total_duration=2.2,
            throughput=68,
            error_status=400,
            error_message="Test error",
            is_streaming=True,
        )

        assert block["reasoning"] == "Test reasoning"
        assert block["content"] == "Test content"
        assert block["tool_calls"] == tool_calls
        assert (
            block["raw"]
            == "<think>Test reasoning</think>Test content<tool_call>tc</tool_call>"
        )
        assert block["streaming"] is True

        # Check error
        assert block["error"]["error_status"] == 400
        assert block["error"]["error_message"] == "Test error"

        # Check usage
        assert block["usage"]["prompt_tokens"] == 100
        assert block["usage"]["completion_tokens"] == 50
        assert block["usage"]["total_tokens"] == 150

        # Check costs (100 * 10/1M + 50 * 30/1M)
        expected_prompt_cost = 100 * (10.0 / 1_000_000)
        expected_completion_cost = 50 * (30.0 / 1_000_000)
        expected_total_cost = expected_prompt_cost + expected_completion_cost

        assert block["cost"]["prompt_cost"] == expected_prompt_cost
        assert block["cost"]["completion_cost"] == expected_completion_cost
        assert block["cost"]["total_cost"] == expected_total_cost

        # Check performance
        assert block["performance"]["latency"] == 2.5
        assert block["performance"]["reasoning_duration"] == 1.0
        assert block["performance"]["content_duration"] == 1.2
        assert block["performance"]["total_duration"] == 2.2
        assert block["performance"]["throughput"] == 68

    def test_agent_to_dict_method(self, sample_agent):
        """Test to_dict method returns correct dictionary representation."""
        agent_dict = sample_agent.to_dict()

        expected_keys = [
            "name",
            "model",
            "provider",
            "token_limits",
            "cost",
            "features",
        ]

        for key in expected_keys:
            assert key in agent_dict

        # Check basic info
        assert agent_dict["name"] == "test_agent"

        # Check model info
        assert agent_dict["model"]["name"] == "gpt-4"
        assert agent_dict["model"]["display_name"] == "GPT-4"
        assert agent_dict["model"]["origin"] == "openai"
        assert agent_dict["model"]["version"] == "0613"

        # Check provider info
        assert agent_dict["provider"]["name"] == "test_provider"
        assert (
            agent_dict["provider"]["url"] == "https://api.test.com/v1/chat/completions"
        )

        # Check token limits
        assert agent_dict["token_limits"]["input"] == 8192
        assert agent_dict["token_limits"]["output"] == 4096

        # Check cost info
        assert agent_dict["cost"]["per_token"]["input"] == 10.0 / 1_000_000
        assert agent_dict["cost"]["per_token"]["output"] == 30.0 / 1_000_000
        assert agent_dict["cost"]["per_1m_tokens"]["input"] == 10.0
        assert agent_dict["cost"]["per_1m_tokens"]["output"] == 30.0

        # Check features
        assert agent_dict["features"]["supports_tools"] is True
        assert agent_dict["features"]["supports_reasoning"] is True
        assert agent_dict["features"]["reasoning_tokens_access"] is True

    def test_agent_str_method(self, sample_agent):
        """Test __str__ method returns JSON string."""
        import json

        agent_str = str(sample_agent)

        # Should be valid JSON
        agent_dict = json.loads(agent_str)

        # Should match to_dict output
        assert agent_dict == sample_agent.to_dict()

    def test_agent_model_without_version(self):
        """Test Agent with model that has no version."""
        model = Model(
            name="claude-3-sonnet", display_name="Claude 3 Sonnet", origin="anthropic"
        )

        provider = Provider(
            name="test_provider", url="https://api.test.com/v1/chat/completions"
        )

        agent = Agent(
            name="test_agent",
            model=model,
            provider=provider,
            max_input_tokens=100000,
            max_output_tokens=4096,
            cost_per_1m_input_tokens=3.0,
            cost_per_1m_output_tokens=15.0,
        )

        # Check that version is None
        assert agent.model.version is None

        # Check block includes None version
        block = agent._block()
        assert block["model"]["version"] is None

        # Check to_dict includes None version
        agent_dict = agent.to_dict()
        assert agent_dict["model"]["version"] is None
