# standard
# third party
# custom
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.models.deepseek import *
from sunwaee.aegen.providers.deepseek import *


DEEPSEEK_REASONER_AGENT = Agent(
    name="deepseek/deepseek-reasoner",
    model=DEEPSEEK_REASONER,
    provider=DEEPSEEK,
    max_input_tokens=128000,
    max_output_tokens=64000,
    cost_per_1m_input_tokens=0.56,
    cost_per_1m_output_tokens=1.68,
    supports_tools=False,
    supports_reasoning=True,
    reasoning_tokens_access=True,
)

DEEPSEEK_CHAT_AGENT = Agent(
    name="deepseek/deepseek-chat",
    model=DEEPSEEK_CHAT,
    provider=DEEPSEEK,
    max_input_tokens=128000,
    max_output_tokens=64000,
    cost_per_1m_input_tokens=0.56,
    cost_per_1m_output_tokens=1.68,
    supports_tools=True,
    supports_reasoning=False,
    reasoning_tokens_access=False,
)

DEEPSEEK_AGENTS = [
    DEEPSEEK_REASONER_AGENT,
    DEEPSEEK_CHAT_AGENT,
]
