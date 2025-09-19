# standard
# third party
# custom
from sunwaee.aegen import agents
from sunwaee.aegen import models
from sunwaee.aegen import providers
from sunwaee.aegen.agents._registry import AGENTS
from sunwaee.aegen.models._registry import MODELS
from sunwaee.aegen.providers._registry import PROVIDERS
from sunwaee.aegen.agent import Agent
from sunwaee.aegen.model import Model
from sunwaee.aegen.provider import Provider


async def async_completion(
    agent: str | Agent,
    messages: list[dict],
    tools: list[dict] | None = None,
    streaming: bool = False,
):
    if isinstance(agent, str):
        if agent not in AGENTS:
            available_agents = list(AGENTS.keys())
            raise ValueError(
                f"Agent '{agent}' not found. Available agents: {available_agents}"
            )
        agent_obj = AGENTS[agent]
    else:
        agent_obj = agent

    async for block in agent_obj.async_completion(
        messages=messages,
        tools=tools,
        streaming=streaming,
    ):
        yield block


__all__ = [
    "AGENTS",
    "MODELS",
    "PROVIDERS",
    "Agent",
    "Model",
    "Provider",
    "agents",
    "models",
    "providers",
    "async_completion",
]
