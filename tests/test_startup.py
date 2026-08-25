from __future__ import annotations

import importlib
import sys
import textwrap
import types
from typing import TYPE_CHECKING, Any

import pytest
import trio

from tlserver.config import AppSettings

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

ROOT_PORT = 19000
TRANSLATOR_PORT = 19001


def _write_minimal_config(tmp_path: Path) -> Path:
    config_text = textwrap.dedent(
        f"""
        debug = false
        root_port = {ROOT_PORT}

        [[translators]]
        kind = "Offline"
        enabled = true
        port = {TRANSLATOR_PORT}
        """
    ).strip()
    config_path = tmp_path / "config.toml"
    config_path.write_text(config_text)
    return config_path


@pytest.fixture
def config_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    config_path = _write_minimal_config(tmp_path)
    monkeypatch.setenv("TLSERVER_CONFIG_PATH", str(config_path))
    return config_path


@pytest.fixture
def stub_dependencies(monkeypatch: pytest.MonkeyPatch) -> None:
    dummy_ctranslate2 = types.ModuleType("ctranslate2")

    class DummyTranslator:
        """Minimal stand-in for the CTranslate2 translator."""

        def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
            self.args = args
            self.kwargs = kwargs

        def translate_batch(self, *args, **kwargs) -> list:  # noqa: ANN002, ANN003, ARG002
            return []

    dummy_ctranslate2.Translator = DummyTranslator  # pyright: ignore[reportAttributeAccessIssue]
    monkeypatch.setitem(sys.modules, "ctranslate2", dummy_ctranslate2)

    dummy_sentencepiece = types.ModuleType("sentencepiece")

    class DummySentencePieceProcessor:
        """Simplified processor used only for construction tests."""

        def __init__(self, model_path: str) -> None:
            self.model_path = model_path

        def encode(self, text, **kwargs) -> list[list[str]] | list[str]:  # noqa: ANN001, ANN003, ARG002
            if isinstance(text, list):
                return [[str(item)] for item in text]
            return [str(text)]

        def decode(self, text) -> list[str]:  # noqa: ANN001
            if isinstance(text, list):
                return ["".join(map(str, text))]
            return [str(text)]

    dummy_sentencepiece.SentencePieceProcessor = DummySentencePieceProcessor  # pyright: ignore[reportAttributeAccessIssue]
    monkeypatch.setitem(sys.modules, "sentencepiece", dummy_sentencepiece)


@pytest.fixture
def main_module(
    config_env: Path,  # noqa: ARG001
    stub_dependencies: None,  # noqa: ARG001
) -> Generator[types.ModuleType, Any, types.NoneType]:
    """Import tlserver.__main__ with the stubbed environment."""
    for module_name in [
        "tlserver.__main__",
        "tlserver.handler",
        "tlserver.translators.offline",
        "tlserver.config",
    ]:
        sys.modules.pop(module_name, None)

    module = importlib.import_module("tlserver.__main__")
    yield module

    for module_name in [
        "tlserver.__main__",
        "tlserver.handler",
        "tlserver.translators.offline",
        "tlserver.config",
    ]:
        sys.modules.pop(module_name, None)


def test_appsettings_reads_minimal_config(config_env: Path) -> None:  # noqa: ARG001
    settings = AppSettings()  # pyright: ignore[reportCallIssue]

    assert settings.root_port == ROOT_PORT  # noqa: S101
    assert [t.kind for t in settings.translators] == ["Offline"]  # noqa: S101
    assert settings.translators[0].port == TRANSLATOR_PORT  # noqa: S101


def test_handlers_ready(main_module: types.ModuleType) -> None:
    assert len(main_module.handlers) == 1  # noqa: S101

    handler = main_module.handlers[0]
    assert handler.port == TRANSLATOR_PORT  # noqa: S101
    assert handler.translator.is_ready is True  # noqa: S101
    assert main_module.ports == {TRANSLATOR_PORT}  # noqa: S101


def test_amain_configures_hypercorn(
    main_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded: dict[str, object] = {}

    async def fake_serve(app, config, shutdown_trigger) -> None:  # noqa: ANN001
        recorded["bind"] = list(config.bind)
        recorded["app"] = app
        recorded["shutdown"] = shutdown_trigger
        await trio.lowlevel.checkpoint()

    monkeypatch.setattr(main_module, "serve", fake_serve)
    monkeypatch.setattr(main_module.signal, "signal", lambda *args, **kwargs: None)  # noqa: ARG005
    main_module.die = trio.Event()  # pyright: ignore[reportAttributeAccessIssue]

    trio.run(main_module.amain)

    assert recorded["bind"] == [f"0.0.0.0:{TRANSLATOR_PORT}"]  # noqa: S101
    assert callable(recorded["shutdown"])  # noqa: S101
