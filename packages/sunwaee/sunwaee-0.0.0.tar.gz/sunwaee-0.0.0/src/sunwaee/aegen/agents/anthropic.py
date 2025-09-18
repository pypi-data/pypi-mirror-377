# standard
# third party
# custom
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.models.anthropic import *
from sunwaee.aegen.providers.anthropic import ANTHROPIC


CLAUDE_4_1_OPUS_AGENT = Agent(
    name="anthropic/claude-4-1-opus",
    model=CLAUDE_4_1_OPUS,
    provider=ANTHROPIC,
    max_input_tokens=200000,
    max_output_tokens=32000,
    cost_per_1m_input_tokens=15,
    cost_per_1m_output_tokens=75,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

CLAUDE_4_OPUS_AGENT = Agent(
    name="anthropic/claude-4-opus",
    model=CLAUDE_4_OPUS,
    provider=ANTHROPIC,
    max_input_tokens=200000,
    max_output_tokens=32000,
    cost_per_1m_input_tokens=15,
    cost_per_1m_output_tokens=75,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

CLAUDE_4_SONNET_AGENT = Agent(
    name="anthropic/claude-4-sonnet",
    model=CLAUDE_4_SONNET,
    provider=ANTHROPIC,
    max_input_tokens=200000,
    max_output_tokens=64000,
    cost_per_1m_input_tokens=3,
    cost_per_1m_output_tokens=15,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

CLAUDE_3_7_SONNET_AGENT = Agent(
    name="anthropic/claude-3-7-sonnet",
    model=CLAUDE_3_7_SONNET,
    provider=ANTHROPIC,
    max_input_tokens=200000,
    max_output_tokens=64000,
    cost_per_1m_input_tokens=3,
    cost_per_1m_output_tokens=15,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

ANTHROPIC_AGENTS = [
    CLAUDE_4_1_OPUS_AGENT,
    CLAUDE_4_OPUS_AGENT,
    CLAUDE_4_SONNET_AGENT,
    CLAUDE_3_7_SONNET_AGENT,
]
