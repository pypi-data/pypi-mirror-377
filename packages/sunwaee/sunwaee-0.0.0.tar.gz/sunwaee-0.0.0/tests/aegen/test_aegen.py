# standard
import pytest
from unittest.mock import AsyncMock, patch

# third party
# custom
from sunwaee.aegen import async_completion, AGENTS


class TestAegenAsyncCompletion:
    """Test the top-level async_completion function."""

    @pytest.mark.asyncio
    async def test_async_completion_invalid_agent_name(self):
        """Test that invalid agent names raise ValueError with helpful message."""
        messages = [{"role": "user", "content": "Hello"}]

        with pytest.raises(ValueError) as exc_info:
            async for block in async_completion("invalid/agent-name", messages):
                break

        error_message = str(exc_info.value)
        assert "Agent 'invalid/agent-name' not found" in error_message
        assert "Available agents:" in error_message
        # Should list some real agent names
        assert (
            "anthropic/claude-4-sonnet" in error_message
            or "openai/gpt-5" in error_message
        )

    @pytest.mark.asyncio
    async def test_async_completion_non_streaming_success(self, sample_tools):
        """Test successful non-streaming completion with parameter forwarding."""
        # Mock response block
        mock_block = {
            "model": {"name": "gpt-5", "display_name": "GPT 5"},
            "provider": {
                "name": "openai",
                "url": "https://api.openai.com/v1/chat/completions",
            },
            "reasoning": "I need to think about this carefully.",
            "content": "Here's my response based on the analysis.",
            "tool_calls": [
                {
                    "id": "call_123",
                    "name": {"name": "search_codebase"},
                    "arguments": {
                        "name": "search_codebase",
                        "arguments": '{"query": "test"}',
                    },
                }
            ],
            "raw": "I need to think about this carefully.\n\nHere's my response based on the analysis.",
            "error": {"error_status": 0, "error_message": None},
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            "cost": {
                "prompt_cost": 0.001,
                "completion_cost": 0.002,
                "total_cost": 0.003,
            },
            "performance": {
                "latency": 0.5,
                "reasoning_duration": 0.2,
                "content_duration": 0.3,
                "total_duration": 0.5,
                "throughput": 100,
            },
            "streaming": False,
        }

        # Get the actual agent from registry
        agent_name = "openai/gpt-5"
        agent = AGENTS[agent_name]

        # Mock the agent's async_completion method
        with patch.object(agent, "async_completion") as mock_agent_completion:
            # Configure mock to yield the response block
            async def mock_async_generator():
                yield mock_block

            mock_agent_completion.return_value = mock_async_generator()

            messages = [{"role": "user", "content": "Explain machine learning"}]

            # Execute the top-level async_completion function
            blocks = []
            async for block in async_completion(
                agent_name, messages, tools=sample_tools, streaming=False
            ):
                blocks.append(block)

            # Verify we got the expected response
            assert len(blocks) == 1
            assert blocks[0] == mock_block

            # Verify the agent's async_completion was called with correct parameters
            mock_agent_completion.assert_called_once_with(
                messages=messages,
                tools=sample_tools,
                streaming=False,
            )

    @pytest.mark.asyncio
    async def test_async_completion_streaming_success(self, sample_tools):
        """Test successful streaming completion with multiple blocks."""
        # Mock multiple streaming blocks
        mock_blocks = [
            {
                "model": {"name": "claude-sonnet-4", "display_name": "Claude Sonnet 4"},
                "provider": {
                    "name": "anthropic",
                    "url": "https://api.anthropic.com/v1/messages",
                },
                "reasoning": "Let me think",
                "content": "",
                "tool_calls": [],
                "raw": "Let me think",
                "error": {"error_status": 0, "error_message": None},
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "cost": {"prompt_cost": 0.0, "completion_cost": 0.0, "total_cost": 0.0},
                "performance": {
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "content_duration": 0.0,
                    "total_duration": 0.0,
                    "throughput": 0,
                },
                "streaming": True,
            },
            {
                "model": {"name": "claude-sonnet-4", "display_name": "Claude Sonnet 4"},
                "provider": {
                    "name": "anthropic",
                    "url": "https://api.anthropic.com/v1/messages",
                },
                "reasoning": "Let me think about this problem.",
                "content": "Based on my analysis",
                "tool_calls": [],
                "raw": "Let me think about this problem.\n\nBased on my analysis",
                "error": {"error_status": 0, "error_message": None},
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0,
                },
                "cost": {"prompt_cost": 0.0, "completion_cost": 0.0, "total_cost": 0.0},
                "performance": {
                    "latency": 0.0,
                    "reasoning_duration": 0.0,
                    "content_duration": 0.0,
                    "total_duration": 0.0,
                    "throughput": 0,
                },
                "streaming": True,
            },
            {
                "model": {"name": "claude-sonnet-4", "display_name": "Claude Sonnet 4"},
                "provider": {
                    "name": "anthropic",
                    "url": "https://api.anthropic.com/v1/messages",
                },
                "reasoning": "Let me think about this problem carefully.",
                "content": "Based on my analysis, here's the complete answer.",
                "tool_calls": [
                    {
                        "id": "call_456",
                        "name": "search_codebase",
                        "arguments": {"query": "authentication system"},
                    }
                ],
                "raw": "Let me think about this problem carefully.\n\nBased on my analysis, here's the complete answer.",
                "error": {"error_status": 0, "error_message": None},
                "usage": {
                    "prompt_tokens": 75,
                    "completion_tokens": 125,
                    "total_tokens": 200,
                },
                "cost": {
                    "prompt_cost": 0.0015,
                    "completion_cost": 0.0025,
                    "total_cost": 0.004,
                },
                "performance": {
                    "latency": 1.2,
                    "reasoning_duration": 0.5,
                    "content_duration": 0.7,
                    "total_duration": 1.2,
                    "throughput": 104,
                },
                "streaming": True,
            },
        ]

        # Get the actual agent from registry
        agent_name = "anthropic/claude-4-sonnet"
        agent = AGENTS[agent_name]

        # Mock the agent's async_completion method
        with patch.object(agent, "async_completion") as mock_agent_completion:
            # Configure mock to yield multiple blocks
            async def mock_async_generator():
                for block in mock_blocks:
                    yield block

            mock_agent_completion.return_value = mock_async_generator()

            messages = [
                {"role": "user", "content": "Help me debug this authentication issue"}
            ]

            # Execute the top-level async_completion function
            blocks = []
            async for block in async_completion(
                agent_name, messages, tools=sample_tools, streaming=True
            ):
                blocks.append(block)

            # Verify we got all expected response blocks
            assert len(blocks) == 3
            assert blocks == mock_blocks

            # Verify the agent's async_completion was called with correct parameters
            mock_agent_completion.assert_called_once_with(
                messages=messages,
                tools=sample_tools,
                streaming=True,
            )

    @pytest.mark.asyncio
    async def test_async_completion_without_tools(self):
        """Test completion without tools parameter."""
        mock_block = {
            "model": {"name": "gpt-4-1", "display_name": "GPT 4.1"},
            "provider": {
                "name": "openai",
                "url": "https://api.openai.com/v1/chat/completions",
            },
            "reasoning": None,
            "content": "Simple response without tools.",
            "tool_calls": [],
            "raw": "Simple response without tools.",
            "error": {"error_status": 0, "error_message": None},
            "usage": {"prompt_tokens": 25, "completion_tokens": 15, "total_tokens": 40},
            "cost": {
                "prompt_cost": 0.0005,
                "completion_cost": 0.0003,
                "total_cost": 0.0008,
            },
            "performance": {
                "latency": 0.3,
                "reasoning_duration": 0.0,
                "content_duration": 0.3,
                "total_duration": 0.3,
                "throughput": 50,
            },
            "streaming": False,
        }

        # Get the actual agent from registry
        agent_name = "openai/gpt-4-1"
        agent = AGENTS[agent_name]

        # Mock the agent's async_completion method
        with patch.object(agent, "async_completion") as mock_agent_completion:
            # Configure mock to yield the response block
            async def mock_async_generator():
                yield mock_block

            mock_agent_completion.return_value = mock_async_generator()

            messages = [{"role": "user", "content": "What is Python?"}]

            # Execute without tools parameter (should default to None)
            blocks = []
            async for block in async_completion(agent_name, messages):
                blocks.append(block)

            # Verify we got the expected response
            assert len(blocks) == 1
            assert blocks[0] == mock_block

            # Verify the agent's async_completion was called with tools=None and streaming=False (defaults)
            mock_agent_completion.assert_called_once_with(
                messages=messages,
                tools=None,
                streaming=False,
            )

    @pytest.mark.asyncio
    async def test_async_completion_parameter_combinations(self):
        """Test various parameter combinations are forwarded correctly."""
        mock_block = {
            "model": {"name": "grok-4", "display_name": "Grok 4"},
            "provider": {"name": "xai", "url": "https://api.x.ai/v1/chat/completions"},
            "reasoning": "Quick analysis needed.",
            "content": "Here's the answer.",
            "tool_calls": [],
            "raw": "Quick analysis needed.\n\nHere's the answer.",
            "error": {"error_status": 0, "error_message": None},
            "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
            "cost": {
                "prompt_cost": 0.001,
                "completion_cost": 0.0006,
                "total_cost": 0.0016,
            },
            "performance": {
                "latency": 0.4,
                "reasoning_duration": 0.1,
                "content_duration": 0.3,
                "total_duration": 0.4,
                "throughput": 75,
            },
            "streaming": True,
        }

        # Get the actual agent from registry
        agent_name = "xai/grok-4"
        agent = AGENTS[agent_name]

        # Test cases with different parameter combinations
        test_cases = [
            # (tools, streaming, expected_tools, expected_streaming)
            (None, False, None, False),
            (None, True, None, True),
            ([], False, [], False),
            ([], True, [], True),
        ]

        for tools, streaming, expected_tools, expected_streaming in test_cases:
            with patch.object(agent, "async_completion") as mock_agent_completion:
                # Configure mock to yield the response block
                async def mock_async_generator():
                    yield mock_block

                mock_agent_completion.return_value = mock_async_generator()

                messages = [
                    {
                        "role": "user",
                        "content": f"Test with tools={tools}, streaming={streaming}",
                    }
                ]

                # Execute with specific parameter combination
                blocks = []
                async for block in async_completion(
                    agent_name, messages, tools=tools, streaming=streaming
                ):
                    blocks.append(block)

                # Verify the call
                mock_agent_completion.assert_called_once_with(
                    messages=messages,
                    tools=expected_tools,
                    streaming=expected_streaming,
                )

    @pytest.mark.asyncio
    async def test_async_completion_error_handling(self):
        """Test that errors from agent.async_completion are properly propagated."""
        # Get the actual agent from registry
        agent_name = "anthropic/claude-4-sonnet"
        agent = AGENTS[agent_name]

        # Mock the agent's async_completion method to raise an exception
        with patch.object(agent, "async_completion") as mock_agent_completion:
            # Configure mock to raise an exception
            mock_agent_completion.side_effect = RuntimeError("Simulated agent error")

            messages = [{"role": "user", "content": "This will cause an error"}]

            # Verify that the exception is propagated
            with pytest.raises(RuntimeError, match="Simulated agent error"):
                async for block in async_completion(agent_name, messages):
                    break

    @pytest.mark.asyncio
    async def test_async_completion_empty_response(self):
        """Test handling of empty response from agent."""
        # Get the actual agent from registry
        agent_name = "openai/gpt-5-mini"
        agent = AGENTS[agent_name]

        # Mock the agent's async_completion method to yield nothing
        with patch.object(agent, "async_completion") as mock_agent_completion:
            # Configure mock to yield no blocks
            async def mock_empty_generator():
                return
                yield  # unreachable, but makes it a generator

            mock_agent_completion.return_value = mock_empty_generator()

            messages = [{"role": "user", "content": "Empty response test"}]

            # Execute and verify we get no blocks
            blocks = []
            async for block in async_completion(agent_name, messages):
                blocks.append(block)

            assert len(blocks) == 0

            # Verify the agent's async_completion was called
            mock_agent_completion.assert_called_once_with(
                messages=messages,
                tools=None,
                streaming=False,
            )

    @pytest.mark.asyncio
    async def test_async_completion_with_agent_object(self, sample_tools):
        """Test async_completion with Agent object instead of string name."""
        # Mock response block
        mock_block = {
            "model": {"name": "gpt-5", "display_name": "GPT 5"},
            "provider": {
                "name": "openai",
                "url": "https://api.openai.com/v1/chat/completions",
            },
            "reasoning": None,
            "content": "Response using agent object",
            "tool_calls": [],
            "raw": "Response using agent object",
            "error": {"error_status": 0, "error_message": None},
            "usage": {"prompt_tokens": 30, "completion_tokens": 20, "total_tokens": 50},
            "cost": {
                "prompt_cost": 0.0006,
                "completion_cost": 0.0004,
                "total_cost": 0.001,
            },
            "performance": {
                "latency": 0.8,
                "reasoning_duration": 0.0,
                "content_duration": 0.8,
                "total_duration": 0.8,
                "throughput": 25,
            },
            "streaming": False,
        }

        # Get the actual agent from registry
        agent_obj = AGENTS["openai/gpt-5"]

        # Mock the agent's async_completion method
        with patch.object(agent_obj, "async_completion") as mock_agent_completion:
            # Configure mock to yield the response block
            async def mock_async_generator():
                yield mock_block

            mock_agent_completion.return_value = mock_async_generator()

            messages = [{"role": "user", "content": "Test with agent object"}]

            # Execute with Agent object instead of string
            blocks = []
            async for block in async_completion(
                agent_obj, messages, tools=sample_tools, streaming=False
            ):
                blocks.append(block)

            # Verify we got the expected response
            assert len(blocks) == 1
            assert blocks[0] == mock_block

            # Verify the agent's async_completion was called with correct parameters
            mock_agent_completion.assert_called_once_with(
                messages=messages,
                tools=sample_tools,
                streaming=False,
            )

    @pytest.mark.asyncio
    async def test_async_completion_with_custom_agent(self):
        """Test async_completion with a custom Agent object."""
        from sunwaee.aegen import Agent, Model, Provider

        # Create a custom agent
        custom_model = Model("test-model", "Test Model", "test")
        custom_provider = Provider("test", "https://api.test.com/v1/chat/completions")
        custom_agent = Agent(
            name="test/test-model",
            model=custom_model,
            provider=custom_provider,
            max_input_tokens=1000,
            max_output_tokens=500,
            cost_per_1m_input_tokens=1.0,
            cost_per_1m_output_tokens=2.0,
        )

        # Mock response for custom agent
        mock_block = {
            "model": {"name": "test-model", "display_name": "Test Model"},
            "provider": {
                "name": "test",
                "url": "https://api.test.com/v1/chat/completions",
            },
            "reasoning": None,
            "content": "Custom agent response",
            "tool_calls": [],
            "raw": "Custom agent response",
            "error": {"error_status": 0, "error_message": None},
            "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            "cost": {
                "prompt_cost": 0.00001,
                "completion_cost": 0.00001,
                "total_cost": 0.00002,
            },
            "performance": {
                "latency": 0.5,
                "reasoning_duration": 0.0,
                "content_duration": 0.5,
                "total_duration": 0.5,
                "throughput": 10,
            },
            "streaming": False,
        }

        # Mock the custom agent's async_completion method
        with patch.object(custom_agent, "async_completion") as mock_custom_completion:
            # Configure mock to yield the response block
            async def mock_async_generator():
                yield mock_block

            mock_custom_completion.return_value = mock_async_generator()

            messages = [{"role": "user", "content": "Test with custom agent"}]

            # Execute with custom Agent object
            blocks = []
            async for block in async_completion(custom_agent, messages):
                blocks.append(block)

            # Verify we got the expected response
            assert len(blocks) == 1
            assert blocks[0] == mock_block

            # Verify the custom agent's async_completion was called
            mock_custom_completion.assert_called_once_with(
                messages=messages,
                tools=None,
                streaming=False,
            )

    def test_agents_registry_populated(self):
        """Test that the AGENTS registry is properly populated with expected agents."""
        # Verify registry is not empty
        assert len(AGENTS) > 0

        # Verify some expected agent names exist
        expected_agents = [
            "anthropic/claude-4-sonnet",
            "openai/gpt-5",
            "google/gemini-2.5-pro",
            "xai/grok-4",
            "deepseek/deepseek-chat",
        ]

        for agent_name in expected_agents:
            assert (
                agent_name in AGENTS
            ), f"Expected agent '{agent_name}' not found in registry"

            # Verify each agent has the expected interface
            agent = AGENTS[agent_name]
            assert hasattr(
                agent, "async_completion"
            ), f"Agent '{agent_name}' missing async_completion method"
            assert hasattr(
                agent, "name"
            ), f"Agent '{agent_name}' missing name attribute"
            assert hasattr(
                agent, "model"
            ), f"Agent '{agent_name}' missing model attribute"
            assert hasattr(
                agent, "provider"
            ), f"Agent '{agent_name}' missing provider attribute"
