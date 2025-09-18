# standard
import pytest

# third party
# custom
from sunwaee.aegen.providers.openai import openai_headers_adapter


class TestOpenaiProvider:

    def test_openai_headers_adapter_success(self, monkeypatch):
        api_key = "sk-openai-test-key-12345"
        monkeypatch.setenv("OPENAI_API_KEY", api_key)

        headers = openai_headers_adapter()

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        assert headers == expected_headers

    def test_openai_headers_adapter_missing_key(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
            openai_headers_adapter()
