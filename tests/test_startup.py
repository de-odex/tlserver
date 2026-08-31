from __future__ import annotations

import asyncio
import importlib
import json
import logging
import signal
import sys
import textwrap
import types
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import ValidationError

from tlserver.config import AppSettings, LLMTranslatorSettings

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

ROOT_PORT = 19000
TRANSLATOR_PORT = 19001


def _write_minimal_config(tmp_path: Path) -> Path:
    translate_model_path = tmp_path / "models" / "translate"
    translate_model_path.mkdir(parents=True)
    tok_source_model_path = tmp_path / "models" / "spm.ja.model"
    tok_target_model_path = tmp_path / "models" / "spm.en.model"
    tok_source_model_path.touch()
    tok_target_model_path.touch()

    config_path = tmp_path / "config.toml"
    config_path.write_text(
        textwrap.dedent(
            f"""
            debug = false
            root_port = {ROOT_PORT}

            [[translators]]
            kind = "Offline"
            enabled = true
            port = {TRANSLATOR_PORT}
            translate_model_path = {json.dumps(str(translate_model_path))}
            tok_source_model_path = {json.dumps(str(tok_source_model_path))}
            tok_target_model_path = {json.dumps(str(tok_target_model_path))}
            """
        ).strip()
    )
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
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.args = args
            self.kwargs = kwargs

        def translate_batch(self, *_args: object, **_kwargs: object) -> list[object]:
            return []

    dummy_ctranslate2.Translator = DummyTranslator  # pyright: ignore[reportAttributeAccessIssue]
    monkeypatch.setitem(sys.modules, "ctranslate2", dummy_ctranslate2)

    dummy_sentencepiece = types.ModuleType("sentencepiece")

    class DummySentencePieceProcessor:
        def __init__(self, model_path: str) -> None:
            self.model_path = model_path

        def encode(
            self, text: object, **_kwargs: object
        ) -> list[list[str]] | list[str]:
            if isinstance(text, list):
                return [[str(item)] for item in text]
            return [str(text)]

        def decode(self, text: object) -> list[str]:
            return [str(text)]

    dummy_sentencepiece.SentencePieceProcessor = DummySentencePieceProcessor  # pyright: ignore[reportAttributeAccessIssue]
    monkeypatch.setitem(sys.modules, "sentencepiece", dummy_sentencepiece)


@pytest.fixture
def main_module(
    config_env: Path,  # noqa: ARG001
    stub_dependencies: None,  # noqa: ARG001
) -> Generator[types.ModuleType, Any, None]:
    module_names = [
        "tlserver.__main__",
        "tlserver.handler",
        "tlserver.translators.offline",
        "tlserver.config",
    ]
    for module_name in module_names:
        sys.modules.pop(module_name, None)

    module = importlib.import_module("tlserver.__main__")
    yield module

    for module_name in module_names:
        sys.modules.pop(module_name, None)


def test_appsettings_reads_minimal_config(config_env: Path) -> None:  # noqa: ARG001
    settings = AppSettings()  # pyright: ignore[reportCallIssue]

    assert settings.root_port == ROOT_PORT
    assert [translator.kind for translator in settings.translators] == ["Offline"]
    assert settings.translators[0].port == TRANSLATOR_PORT


def test_handlers_ready(main_module: types.ModuleType) -> None:
    assert len(main_module.handlers) == 1
    handler = main_module.handlers[0]
    assert handler.port == TRANSLATOR_PORT
    assert handler.translator.is_ready is True
    assert main_module.ports == {TRANSLATOR_PORT}


def test_shutdown_closes_llm_clients(
    main_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    closed: list[str] = []

    class FakeLLMTranslator:
        async def close(self) -> None:
            closed.append("closed")

    main_module.handlers = [
        types.SimpleNamespace(translator=FakeLLMTranslator()),
        *main_module.handlers,
    ]
    monkeypatch.setattr(main_module, "LLMTranslator", FakeLLMTranslator)

    asyncio.run(main_module.on_stop())

    assert closed == ["closed"]


def test_helpers_format_configuration_errors_and_rich_output(
    main_module: types.ModuleType,
) -> None:
    with pytest.raises(ValidationError) as caught:
        AppSettings(root_port=ROOT_PORT, translators=[{"kind": "unsupported"}])

    text = main_module.format_validation_error(caught.value)

    assert text.startswith("Config validation failed:")
    assert "translators" in text
    assert "hello" in main_module.rich_str({"message": "hello"})


def test_intercept_handler_forwards_standard_log_records(
    main_module: types.ModuleType,
) -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="forwarded message",
        args=(),
        exc_info=None,
    )

    main_module.InterceptHandler().emit(record)


def test_versioned_handlers_selects_legacy_translators(
    main_module: types.ModuleType,
) -> None:
    legacy = main_module.handlers[0]
    modern = types.SimpleNamespace(
        translator=types.SimpleNamespace(
            config=LLMTranslatorSettings(kind="LLM", port=None, path="/modern")
        )
    )

    assert main_module.versioned_handlers(
        [legacy, modern], main_module.Version.LEGACY
    ) == [legacy]
    assert main_module.versioned_handlers([legacy, modern], main_module.Version.V1) == [
        modern
    ]


def test_amain_configures_hypercorn_and_shutdown_signal(
    main_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    recorded: dict[str, object] = {}
    registered_handlers: dict[signal.Signals, object] = {}
    shutdowns: list[str] = []

    async def fake_serve(app: object, config: object, shutdown_trigger: object) -> None:
        recorded["bind"] = list(config.bind)  # pyright: ignore[reportAttributeAccessIssue]
        recorded["app"] = app
        recorded["shutdown"] = shutdown_trigger

    class FakeToken:
        def run_sync_soon(self, callback: object) -> None:
            callback()  # pyright: ignore[reportOperatorIssue]

    def register_signal(sig: signal.Signals, callback: object) -> None:
        registered_handlers[sig] = callback

    monkeypatch.setattr(main_module, "serve", fake_serve)
    monkeypatch.setattr(main_module.trio.lowlevel, "current_trio_token", FakeToken)
    monkeypatch.setattr(
        main_module.signal,
        "signal",
        register_signal,
    )
    main_module.die = types.SimpleNamespace(
        wait=lambda: None, set=lambda: shutdowns.append("set")
    )

    asyncio.run(main_module.amain())
    registered_handlers[signal.SIGINT](signal.SIGINT, None)  # pyright: ignore[operator]

    assert recorded["bind"] == [f"0.0.0.0:{TRANSLATOR_PORT}"]
    assert callable(recorded["shutdown"])
    assert shutdowns == ["set"]


def test_main_starts_trio_runner(
    main_module: types.ModuleType, monkeypatch: pytest.MonkeyPatch
) -> None:
    called: list[object] = []

    def record_runner(target: object) -> None:
        called.append(target)

    monkeypatch.setattr(main_module.trio, "run", record_runner)

    main_module.main()

    assert called == [main_module.amain]
