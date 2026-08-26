from __future__ import annotations

import pytest
from conftest import make_context

from tlserver.config import (
    GlossaryEntry,
    GlossaryProcessorSettings,
    NormalizeProcessorSettings,
    PlaceholderProcessorSettings,
    RegexProcessorSettings,
    ReplaceProcessorSettings,
)
from tlserver.pipeline import TranslationPipeline
from tlserver.processors.glossary import GlossaryProcessor
from tlserver.processors.normalize import NormalizeProcessor
from tlserver.processors.regex import RegexProcessor
from tlserver.processors.replace import ReplaceProcessor


def test_normalize_processor_normalizes_unicode_and_newlines() -> None:
    processor = NormalizeProcessor(
        NormalizeProcessorSettings(kind="normalize", unicode_form="NFC")
    )

    result = processor.process(make_context("e\u0301\r\nnext\rlast"))

    assert result.text == "é\nnext\nlast"


def test_normalize_processor_can_preserve_newlines() -> None:
    processor = NormalizeProcessor(
        NormalizeProcessorSettings(kind="normalize", normalize_newlines=False)
    )

    assert processor.process(make_context("a\r\nb\rc")).text == "a\r\nb\rc"


def test_replace_processor_applies_replacements_in_mapping_order() -> None:
    processor = ReplaceProcessor(
        ReplaceProcessorSettings(
            kind="replace", replacements={"cat": "dog", "dog": "wolf"}
        )
    )

    assert processor.process(make_context("cat dog")).text == "wolf wolf"


def test_regex_processor_substitutes_all_matches() -> None:
    processor = RegexProcessor(
        RegexProcessorSettings(
            kind="regex_replace", pattern=r"(\d+)", replacement=r"[\1]"
        )
    )

    assert processor.process(make_context("HP 25, MP 7")).text == "HP [25], MP [7]"


def test_regex_processor_rejects_invalid_patterns() -> None:
    with pytest.raises(Exception, match="unterminated"):
        RegexProcessor(
            RegexProcessorSettings(kind="regex_replace", pattern="(", replacement="")
        )


def test_glossary_replaces_source_terms_with_placeholders() -> None:
    processor = GlossaryProcessor(
        GlossaryProcessorSettings(
            kind="glossary",
            glossary=[
                GlossaryEntry(source="New", target="Nouveau"),
                GlossaryEntry(source="York", target="York", case_sensitive=False),
                GlossaryEntry(source="New York", target="New York"),
            ],
        )
    )

    result = processor.process(make_context("New York and york"))

    assert result.text == "__TLSERVER_GLOSSARY_2__ and __TLSERVER_GLOSSARY_1__"


def test_glossary_restores_targets_and_rejects_empty_sources() -> None:
    processor = GlossaryProcessor(
        GlossaryProcessorSettings(
            kind="glossary",
            glossary=[
                GlossaryEntry(source="Alice", target="Alicia"),
                GlossaryEntry(source="Bob", target="Roberto"),
            ],
        )
    )

    assert (
        processor.process(
            make_context("Hello __TLSERVER_GLOSSARY_0__!", phase="post")
        ).text
        == "Hello Alicia!"
    )
    with pytest.raises(ValueError, match="must not be empty"):
        GlossaryProcessor(
            GlossaryProcessorSettings(
                kind="glossary", glossary=[GlossaryEntry(source="", target="x")]
            )
        )


def test_pipeline_runs_enabled_processors_and_preserves_context_history() -> None:
    pipeline = TranslationPipeline(
        preprocessors=[
            NormalizeProcessorSettings(kind="normalize"),
            ReplaceProcessorSettings(kind="replace", replacements={"é": "E"}),
            RegexProcessorSettings(
                kind="regex_replace", pattern="skip", replacement="used", enabled=False
            ),
            GlossaryProcessorSettings(
                kind="glossary", glossary=[GlossaryEntry(source="Hero", target="Héro")]
            ),
        ],
        postprocessors=[
            GlossaryProcessorSettings(
                kind="glossary", glossary=[GlossaryEntry(source="Hero", target="Héro")]
            ),
            ReplaceProcessorSettings(
                kind="replace", replacements={"translated": "done"}
            ),
        ],
    )

    preprocessed = pipeline.preprocess("e\u0301\r\nHero", "Japanese", "English")
    postprocessed = pipeline.postprocess(
        preprocessed, "translated __TLSERVER_GLOSSARY_0__"
    )

    assert preprocessed.source_text == "e\u0301\r\nHero"
    assert preprocessed.preprocessed_text == "E\n__TLSERVER_GLOSSARY_0__"
    assert preprocessed.translated_text == ""
    assert postprocessed.preprocessed_text == "E\n__TLSERVER_GLOSSARY_0__"
    assert postprocessed.translated_text == "translated __TLSERVER_GLOSSARY_0__"
    assert postprocessed.postprocessed_text == "done Héro"


def test_pipeline_ignores_disabled_and_unimplemented_processors() -> None:
    pipeline = TranslationPipeline(
        preprocessors=[
            ReplaceProcessorSettings(
                kind="replace", replacements={"before": "after"}, enabled=False
            ),
            PlaceholderProcessorSettings(kind="placeholder"),
        ]
    )

    assert pipeline.preprocess("before", "Japanese", "English").text == "before"
