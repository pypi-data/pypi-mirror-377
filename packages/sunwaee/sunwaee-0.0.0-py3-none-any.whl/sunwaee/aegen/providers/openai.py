# standard
import os

# third party
# custom
from sunwaee.aegen.provider import Provider


def openai_headers_adapter(**kwargs) -> dict:
    """
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }
    """

    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is not set")

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
    }


OPENAI = Provider(
    name="openai",
    url="https://api.openai.com/v1/chat/completions",
    headers_adapter=openai_headers_adapter,
)
