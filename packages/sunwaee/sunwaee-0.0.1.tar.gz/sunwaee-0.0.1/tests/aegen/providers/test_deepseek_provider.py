# standard
import pytest

# third party
# custom
from sunwaee.aegen.providers.deepseek import deepseek_headers_adapter


class TestDeepseekProvider:

    def test_deepseek_headers_adapter_success(self, monkeypatch):
        api_key = "sk-deepseek-test-key-12345"
        monkeypatch.setenv("DEEPSEEK_API_KEY", api_key)

        headers = deepseek_headers_adapter()

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        assert headers == expected_headers

    def test_deepseek_headers_adapter_missing_key(self, monkeypatch):
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with pytest.raises(ValueError, match="DEEPSEEK_API_KEY is not set"):
            deepseek_headers_adapter()
