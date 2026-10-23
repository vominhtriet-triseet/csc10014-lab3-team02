import pytest

from assistant_core.config import load_settings
from assistant_core.errors import ConfigError


def test_load_settings_defaults(monkeypatch):
    for name in (
        "ASSISTANT_DATA_DIR",
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "CREDIT_RATE_VND",
        "RETAKE_MULTIPLIER",
        "MAX_CREDITS",
        "LOG_LEVEL",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = load_settings(env_file=None)

    assert settings.llm_provider == "stub"
    assert settings.credit_rate_vnd == 450_000
    assert settings.retake_multiplier == 1.5
    assert settings.max_credits == 30


def test_template_provider_does_not_require_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "template")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    settings = load_settings(env_file=None)

    assert settings.llm_provider == "template"
    assert settings.llm_api_key is None


def test_invalid_numeric_setting_raises_config_error(monkeypatch):
    monkeypatch.setenv("MAX_CREDITS", "many")

    with pytest.raises(ConfigError, match="invalid type"):
        load_settings(env_file=None)


def test_external_provider_requires_api_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "remote")
    monkeypatch.delenv("LLM_API_KEY", raising=False)

    with pytest.raises(ConfigError, match="LLM_API_KEY is required"):
        load_settings(env_file=None)


def test_invalid_log_level_raises_config_error(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(ConfigError, match="Invalid LOG_LEVEL"):
        load_settings(env_file=None)
