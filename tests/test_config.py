from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from tlserver.config import (
    AppSettings,
    LLMTranslatorSettings,
    OfflineTranslatorSettings,
    Version,
    find_config_path,
)


def test_find_config_path_uses_environment_before_other_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    configured = tmp_path / "explicit.toml"
    configured.write_text("root_port = 9999")
    xdg_config = tmp_path / "xdg" / "tlserver" / "config.toml"
    xdg_config.parent.mkdir(parents=True)
    xdg_config.write_text("root_port = 8888")
    monkeypatch.setenv("TLSERVER_CONFIG_PATH", str(configured))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))

    assert find_config_path() == configured


def test_find_config_path_returns_none_when_no_candidate_exists(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("TLSERVER_CONFIG_PATH", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("APPDATA", raising=False)
    monkeypatch.chdir(tmp_path)

    assert find_config_path() is None


def test_app_settings_loads_toml_and_environment_overrides_it(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "root_port = 19000\n[[translators]]\nkind = 'LLM'\nport = 19001\n"
    )
    monkeypatch.setenv("TLSERVER_CONFIG_PATH", str(config_path))
    monkeypatch.setenv("TLSERVER_ROOT_PORT", "19002")

    settings = AppSettings()  # pyright: ignore[reportCallIssue]

    assert settings.root_port == 19002
    assert isinstance(settings.translators[0], LLMTranslatorSettings)
    assert settings.translators[0].port == 19001


def test_disabled_offline_translator_skips_missing_model_path_validation() -> None:
    settings = AppSettings(
        root_port=19000,
        translators=[
            {
                "kind": "Offline",
                "enabled": False,
                "translate_model_path": "/does/not/exist",
                "tok_source_model_path": "/does/not/exist",
                "tok_target_model_path": "/does/not/exist",
            }
        ],
    )

    assert settings.translators[0].enabled is False


@pytest.mark.parametrize(
    ("translators", "message"),
    [
        ([{"kind": "LLM", "port": None, "path": None}], "At least one"),
        (
            [{"kind": "LLM", "port": 19001}, {"kind": "Google", "port": 19001}],
            "Duplicate plugin ports",
        ),
        (
            [{"kind": "LLM", "path": "/a"}, {"kind": "Google", "path": "/a"}],
            "Duplicate plugin paths",
        ),
    ],
)
def test_app_settings_rejects_invalid_handler_mappings(
    translators: list[dict[str, object]], message: str
) -> None:
    with pytest.raises(ValidationError, match=message):
        AppSettings(root_port=19000, translators=translators)


def test_disabled_translator_does_not_participate_in_duplicate_detection() -> None:
    settings = AppSettings(
        root_port=19000,
        translators=[
            {"kind": "LLM", "port": 19001},
            {"kind": "Google", "port": 19001, "enabled": False},
        ],
    )

    assert len(settings.translators) == 2


def test_settings_forbid_unknown_fields_and_apply_defaults() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        LLMTranslatorSettings(kind="LLM", port=19001, unexpected=True)  # pyright: ignore[reportCallIssue]

    settings = LLMTranslatorSettings(kind="LLM", port=19001)
    assert settings.input_language == "Japanese"
    assert settings.supported_languages["German"] == "German"


def test_version_classifies_port_and_path_configurations() -> None:
    legacy = LLMTranslatorSettings(kind="LLM", port=19001)
    modern = LLMTranslatorSettings(kind="LLM", port=None, path="/translate")
    offline = OfflineTranslatorSettings(kind="Offline", enabled=False, port=19002)

    assert Version.LEGACY.applies(legacy)
    assert not Version.V1.applies(legacy)
    assert Version.V1.applies(modern)
    assert Version.LEGACY.applies(offline)
