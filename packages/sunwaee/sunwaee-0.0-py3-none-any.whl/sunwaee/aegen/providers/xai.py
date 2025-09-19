# standard
import os

# third party
# custom
from sunwaee.aegen.provider import Provider


def xai_headers_adapter(**kwargs) -> dict:
    """
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
    }
    """

    if not os.getenv("XAI_API_KEY"):
        raise ValueError("XAI_API_KEY is not set")

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('XAI_API_KEY')}",
    }


XAI = Provider(
    name="xai",
    url="https://api.x.ai/v1/chat/completions",
    headers_adapter=xai_headers_adapter,
)
