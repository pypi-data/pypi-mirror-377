# standard
import pytest

# third party
# custom
from sunwaee.aegen.providers.xai import xai_headers_adapter


class TestXaiProvider:

    def test_xai_headers_adapter_success(self, monkeypatch):
        api_key = "xai-test-key-12345"
        monkeypatch.setenv("XAI_API_KEY", api_key)

        headers = xai_headers_adapter()

        expected_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        assert headers == expected_headers

    def test_xai_headers_adapter_missing_key(self, monkeypatch):
        monkeypatch.delenv("XAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="XAI_API_KEY is not set"):
            xai_headers_adapter()
