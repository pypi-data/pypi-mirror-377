# standard
# third party
# custom
from sunwaee.logger import logger
from sunwaee.aegen.models.anthropic import *
from sunwaee.aegen.models.deepseek import *
from sunwaee.aegen.models.google import *
from sunwaee.aegen.models.openai import *
from sunwaee.aegen.models.xai import *

MODELS = {
    m.name: m
    for m in ANTHROPIC_MODELS
    + DEEPSEEK_MODELS
    + GOOGLE_MODELS
    + OPENAI_MODELS
    + XAI_MODELS
}

logger.info(f"AVAILABLE MODELS: {MODELS.keys()}")
