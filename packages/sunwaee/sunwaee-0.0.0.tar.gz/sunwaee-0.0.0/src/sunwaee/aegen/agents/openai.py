# standard
# third party
# custom
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.models.openai import *
from sunwaee.aegen.providers.openai import *

GPT_5_AGENT = Agent(
    name="openai/gpt-5",
    model=GPT_5,
    provider=OPENAI,
    max_input_tokens=400000,
    max_output_tokens=128000,
    cost_per_1m_input_tokens=1.25,
    cost_per_1m_output_tokens=10,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GPT_5_MINI_AGENT = Agent(
    name="openai/gpt-5-mini",
    model=GPT_5_MINI,
    provider=OPENAI,
    max_input_tokens=400000,
    max_output_tokens=128000,
    cost_per_1m_input_tokens=0.25,
    cost_per_1m_output_tokens=2,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GPT_5_NANO_AGENT = Agent(
    name="openai/gpt-5-nano",
    model=GPT_5_NANO,
    provider=OPENAI,
    max_input_tokens=400000,
    max_output_tokens=128000,
    cost_per_1m_input_tokens=0.05,
    cost_per_1m_output_tokens=0.4,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GPT_4_1_AGENT = Agent(
    name="openai/gpt-4-1",
    model=GPT_4_1,
    provider=OPENAI,
    max_input_tokens=1048576,
    max_output_tokens=32768,
    cost_per_1m_input_tokens=3,
    cost_per_1m_output_tokens=12,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GPT_4_1_MINI_AGENT = Agent(
    name="openai/gpt-4-1-mini",
    model=GPT_4_1_MINI,
    provider=OPENAI,
    max_input_tokens=1048576,
    max_output_tokens=32768,
    cost_per_1m_input_tokens=0.8,
    cost_per_1m_output_tokens=3.2,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GPT_4_1_NANO_AGENT = Agent(
    name="openai/gpt-4-1-nano",
    model=GPT_4_1_NANO,
    provider=OPENAI,
    max_input_tokens=1048576,
    max_output_tokens=32768,
    cost_per_1m_input_tokens=0.2,
    cost_per_1m_output_tokens=0.8,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

OPENAI_AGENTS = [
    GPT_5_AGENT,
    GPT_5_MINI_AGENT,
    GPT_5_NANO_AGENT,
    GPT_4_1_AGENT,
    GPT_4_1_MINI_AGENT,
    GPT_4_1_NANO_AGENT,
]
