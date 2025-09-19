# standard
# third party
# custom
from sunwaee.aegen import Model


class TestModel:

    def test_model_initialization_required_params(self):
        """Test Model initialization with required parameters."""
        model = Model(name="gpt-4", display_name="GPT-4", origin="openai")

        assert model.name == "gpt-4"
        assert model.display_name == "GPT-4"
        assert model.origin == "openai"
        assert model.version is None

    def test_model_initialization_with_version(self):
        """Test Model initialization with version parameter."""
        model = Model(
            name="claude-3-sonnet",
            display_name="Claude 3 Sonnet",
            origin="anthropic",
            version="20240229",
        )

        assert model.name == "claude-3-sonnet"
        assert model.display_name == "Claude 3 Sonnet"
        assert model.origin == "anthropic"
        assert model.version == "20240229"
