from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import ClassVar

import pytest
from conftest import run_sync_immediately

from tlserver.config import (
    LLMTranslatorSettings,
    RegexProcessorSettings,
    ReplaceProcessorSettings,
)
from tlserver.translators import llm as llm_module
from tlserver.translators import offline as offline_module
from tlserver.translators.llm import LLMTranslator
from tlserver.translators.offline import (
    OfflineTranslator,
    detokenize_batch,
    tokenize_batch,
)


class FakeSentencePieceProcessor:
    instances: ClassVar[list[str]] = []

    def __init__(self, model_path: str) -> None:
        self.model_path = model_path
        self.instances.append(model_path)

    def encode(self, text: str | list[str], **_: object) -> list[str] | list[list[str]]:
        if isinstance(text, list):
            return [[f"token:{value}"] for value in text]
        return [f"token:{text}"]

    def decode(self, text: list[list[str]] | list[str]) -> list[str]:
        if text and isinstance(text[0], str):
            return [f"decoded:{'|'.join(text)}"]
        return [f"decoded:{'|'.join(tokens)}" for tokens in text]


class FakeCTranslateTranslator:
    instances: ClassVar[list[FakeCTranslateTranslator]] = []

    def __init__(self, *args: object, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs
        self.calls: list[dict[str, object]] = []
        self.instances.append(self)

    def translate_batch(self, **kwargs: object) -> list[SimpleNamespace]:
        self.calls.append(kwargs)
        source = kwargs["source"]
        return [
            SimpleNamespace(hypotheses=[[f"model:{'|'.join(tokens)}"]])
            for tokens in source  # pyright: ignore[reportUnknownVariableType]
        ]


@pytest.fixture
def offline_translator(monkeypatch: pytest.MonkeyPatch) -> OfflineTranslator:
    FakeCTranslateTranslator.instances = []
    FakeSentencePieceProcessor.instances = []
    monkeypatch.setattr(
        offline_module.ctranslate2, "Translator", FakeCTranslateTranslator
    )
    monkeypatch.setattr(
        offline_module.spm, "SentencePieceProcessor", FakeSentencePieceProcessor
    )
    monkeypatch.setattr(offline_module.trio.to_thread, "run_sync", run_sync_immediately)
    return OfflineTranslator(
        offline_module.OfflineTranslatorSettings(
            kind="Offline",
            port=19001,
            preprocessors=[
                ReplaceProcessorSettings(kind="replace", replacements={"raw": "ready"})
            ],
            postprocessors=[
                ReplaceProcessorSettings(
                    kind="replace", replacements={"decoded": "final"}
                )
            ],
        )
    )


def test_tokenize_and_detokenize_delegate_to_sentencepiece(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeSentencePieceProcessor.instances = []
    monkeypatch.setattr(
        offline_module.spm, "SentencePieceProcessor", FakeSentencePieceProcessor
    )

    assert tokenize_batch("one", "source.model") == [["token:one"]]
    assert tokenize_batch(["one", "two"], "source.model") == [
        ["token:one"],
        ["token:two"],
    ]
    assert detokenize_batch([["a", "b"]], "target.model") == ["decoded:a|b"]
    assert FakeSentencePieceProcessor.instances == [
        "source.model",
        "source.model",
        "target.model",
    ]


def test_offline_translator_activates_and_translates_with_pipeline(
    offline_translator: OfflineTranslator,
) -> None:
    assert offline_translator.is_ready is False
    assert offline_translator.activate() is True
    engine = FakeCTranslateTranslator.instances[0]

    translation = asyncio.run(offline_translator.translate("raw"))

    assert offline_translator.is_ready is True
    assert engine.kwargs == {
        "device": "cpu",
        "intra_threads": 0,
        "inter_threads": 4,
    }
    assert translation == "final:model:token:ready"
    assert engine.calls[0]["beam_size"] == 5
    assert engine.calls[0]["disable_unk"] is True


def test_offline_translator_translates_batches_and_honors_pause(
    offline_translator: OfflineTranslator,
) -> None:
    offline_translator.activate()

    assert asyncio.run(offline_translator.translate_batch(["one", "two"])) == [
        "final:model:token:one",
        "final:model:token:two",
    ]
    offline_translator.pause()
    assert (
        asyncio.run(offline_translator.translate("one"))
        == "Translation is paused at the moment"
    )
    assert asyncio.run(offline_translator.translate_batch(["one", "two"])) == [
        "Translation is paused at the moment"
    ]
    offline_translator.resume()
    assert offline_translator.stop_translation is False


def test_offline_language_changes_reflect_capability() -> None:
    translator = OfflineTranslator(
        offline_module.OfflineTranslatorSettings(kind="Offline", port=19001)
    )

    assert translator.check_if_language_available("Japanese") is True
    assert translator.check_if_language_available("French") is False
    assert (
        translator.change_input_language("English")
        == "sorry, this translator can't change languages"
    )
    translator.can_change_language_or_not = True
    assert (
        translator.change_input_language("English")
        == "input language changed to English"
    )
    assert (
        translator.change_output_language("French")
        == "sorry, translator doesn't have this language"
    )


def make_llm_config(**kwargs: object) -> LLMTranslatorSettings:
    return LLMTranslatorSettings(
        kind="LLM",
        port=19002,
        system_prompt="Translate {{ input_language }} to {{ output_language }}",
        **kwargs,
    )


def install_llm_completion_fake(
    monkeypatch: pytest.MonkeyPatch,
) -> list[dict[str, object]]:
    calls: list[dict[str, object]] = []

    def completion(**kwargs: object) -> SimpleNamespace:
        calls.append(kwargs)
        message = kwargs["messages"][-1]["content"]  # pyright: ignore[reportIndexIssue]
        return SimpleNamespace(
            choices=[
                SimpleNamespace(message=SimpleNamespace(content=f"result:{message}"))
            ]
        )

    monkeypatch.setattr(llm_module.litellm, "completion", completion)
    monkeypatch.setattr(llm_module.trio.to_thread, "run_sync", run_sync_immediately)
    return calls


def test_llm_translator_builds_local_request_and_runs_pipeline(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_llm_completion_fake(monkeypatch)
    translator = LLMTranslator(
        make_llm_config(
            preprocessors=[
                ReplaceProcessorSettings(kind="replace", replacements={"raw": "ready"})
            ],
            postprocessors=[
                RegexProcessorSettings(
                    kind="regex_replace", pattern="result:", replacement="done:"
                )
            ],
            temperature=0.2,
        )
    )

    assert translator.system_prompt == "Translate Japanese to English"
    assert translator.activate() is True
    assert asyncio.run(translator.translate("raw")) == "done:ready"
    assert calls[0]["model"] == "lm_studio/sugoi14b"
    assert calls[0]["api_base"] == "http://127.0.0.1:1234/v1"
    assert calls[0]["temperature"] == 0.2
    assert [message["role"] for message in translator.messages] == [
        "system",
        "user",
        "assistant",
    ]


def test_llm_translator_uses_no_api_base_for_remote_models(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = install_llm_completion_fake(monkeypatch)
    translator = LLMTranslator(make_llm_config(is_local=False))

    assert asyncio.run(translator.translate("hello")) == "result:hello"
    assert "api_base" not in calls[0]


def test_llm_batch_pause_context_and_language_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_llm_completion_fake(monkeypatch)
    translator = LLMTranslator(make_llm_config(context_lines=3))

    assert asyncio.run(translator.translate_batch(["one", "two"])) == [
        "result:one",
        "result:two",
    ]
    assert len(translator.messages) == 4
    assert translator.messages[0]["role"] == "system"
    translator.pause()
    assert asyncio.run(translator.translate_batch(["one"])) == [
        "Translation is paused at the moment"
    ]
    translator.resume()
    assert (
        translator.change_output_language("German")
        == "output language changed to German"
    )
    assert translator.messages == [
        {"role": "system", "content": "Translate Japanese to German"}
    ]
    assert (
        translator.change_input_language("Klingon")
        == "sorry, translator doesn't have this language"
    )
