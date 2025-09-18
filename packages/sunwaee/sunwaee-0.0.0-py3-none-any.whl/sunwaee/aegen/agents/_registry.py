# standard
# third party
# custom
from sunwaee.logger import logger
from sunwaee.aegen.agents.anthropic import *
from sunwaee.aegen.agents.deepseek import *
from sunwaee.aegen.agents.google import *
from sunwaee.aegen.agents.openai import *
from sunwaee.aegen.agents.xai import *

AGENTS = {
    a.name: a
    for a in ANTHROPIC_AGENTS
    + DEEPSEEK_AGENTS
    + GOOGLE_AGENTS
    + OPENAI_AGENTS
    + XAI_AGENTS
}

logger.info(f"AVAILABLE AGENTS: {AGENTS.keys()}")
