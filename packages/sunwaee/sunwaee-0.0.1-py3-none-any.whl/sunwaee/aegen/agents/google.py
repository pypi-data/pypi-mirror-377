# standard
# third party
# custom
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.models.google import *
from sunwaee.aegen.providers.google import *

GEMINI_2_5_PRO_AGENT = Agent(
    name="google/gemini-2.5-pro",
    model=GEMINI_2_5_PRO,
    provider=GOOGLE,
    max_input_tokens=1048576,
    max_output_tokens=65536,
    cost_per_1m_input_tokens=1.25,
    cost_per_1m_output_tokens=10,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GEMINI_2_5_FLASH_AGENT = Agent(
    name="google/gemini-2.5-flash",
    model=GEMINI_2_5_FLASH,
    provider=GOOGLE,
    max_input_tokens=1048576,
    max_output_tokens=65536,
    cost_per_1m_input_tokens=0.3,
    cost_per_1m_output_tokens=2.5,
    supports_tools=True,
    supports_reasoning=True,
    reasoning_tokens_access=False,
)

GEMINI_2_5_FLASH_LITE_AGENT = Agent(
    name="google/gemini-2.5-flash-lite",
    model=GEMINI_2_5_FLASH_LITE,
    provider=GOOGLE,
    max_input_tokens=1048576,
    max_output_tokens=65536,
    cost_per_1m_input_tokens=0.1,
    cost_per_1m_output_tokens=0.4,
    supports_tools=True,
    supports_reasoning=False,
    reasoning_tokens_access=False,
)

GOOGLE_AGENTS = [
    GEMINI_2_5_PRO_AGENT,
    GEMINI_2_5_FLASH_AGENT,
    GEMINI_2_5_FLASH_LITE_AGENT,
]
