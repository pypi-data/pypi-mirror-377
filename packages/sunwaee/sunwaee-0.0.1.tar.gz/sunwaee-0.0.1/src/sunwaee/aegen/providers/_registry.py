# standard
# third party
# custom
from sunwaee.logger import logger
from sunwaee.aegen.providers.anthropic import *
from sunwaee.aegen.providers.deepseek import *
from sunwaee.aegen.providers.google import *
from sunwaee.aegen.providers.openai import *
from sunwaee.aegen.providers.xai import *

PROVIDERS = {
    p.name: p
    for p in [
        ANTHROPIC,
        DEEPSEEK,
        GOOGLE,
        OPENAI,
        XAI,
    ]
}

logger.info(f"AVAILABLE PROVIDERS: {PROVIDERS.keys()}")
