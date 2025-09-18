# standard
# third party
# custom
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.models.xai import *
from sunwaee.aegen.providers.xai import *

GROK_CODE_FAST_1_AGENT = Agent(
    name="xai/grok-code-fast-1",
    model=GROK_CODE_FAST_1,
    provider=XAI,
    max_input_tokens=256000,
    max_output_tokens=256000,
    cost_per_1m_input_tokens=0.2,
    cost_per_1m_output_tokens=1.5,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

GROK_4_AGENT = Agent(
    name="xai/grok-4",
    model=GROK_4,
    provider=XAI,
    max_input_tokens=256000,
    max_output_tokens=256000,
    cost_per_1m_input_tokens=3,
    cost_per_1m_output_tokens=15,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GROK_3_AGENT = Agent(
    name="xai/grok-3",
    model=GROK_3,
    provider=XAI,
    max_input_tokens=131072,
    max_output_tokens=131072,
    cost_per_1m_input_tokens=3,
    cost_per_1m_output_tokens=15,
    supports_tools=True,
    supports_reasoning=False,
    reasoning_tokens_access=False,
)

GROK_3_MINI_AGENT = Agent(
    name="xai/grok-3-mini",
    model=GROK_3_MINI,
    provider=XAI,
    max_input_tokens=131072,
    max_output_tokens=131072,
    cost_per_1m_input_tokens=0.3,
    cost_per_1m_output_tokens=0.5,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)


XAI_AGENTS = [
    GROK_CODE_FAST_1_AGENT,
    GROK_4_AGENT,
    GROK_3_AGENT,
    GROK_3_MINI_AGENT,
]
