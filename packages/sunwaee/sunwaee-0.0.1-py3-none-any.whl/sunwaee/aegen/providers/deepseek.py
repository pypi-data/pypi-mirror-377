# standard
import os

# third party
# custom
from sunwaee.aegen.provider import Provider


def deepseek_headers_adapter(**kwargs) -> dict:
    """
    {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
    }
    """

    if not os.getenv("DEEPSEEK_API_KEY"):
        raise ValueError("DEEPSEEK_API_KEY is not set")

    return {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
    }


DEEPSEEK = Provider(
    name="deepseek",
    url="https://api.deepseek.com/v1/chat/completions",
    headers_adapter=deepseek_headers_adapter,
)
