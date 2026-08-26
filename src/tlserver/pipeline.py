from dataclasses import replace
from typing import TypeVar

from tlserver.config import (
    ProcessorSettings,
    TranslatorSettingsBase,
)
from tlserver.processor import Processor, TranslationContext
from tlserver.processors.glossary import GlossaryProcessor
from tlserver.processors.normalize import NormalizeProcessor
from tlserver.processors.regex import RegexProcessor
from tlserver.processors.replace import ReplaceProcessor

ConfigT = TypeVar("ConfigT", bound=TranslatorSettingsBase)


PROCESSOR_CLASSES: dict[str, type[Processor] | None] = {
    "normalize": NormalizeProcessor,
    "replace": ReplaceProcessor,
    "regex_replace": RegexProcessor,
    "glossary": GlossaryProcessor,
    "placeholder": None,
}


class TranslationPipeline:
    preprocessors: list[Processor]
    postprocessors: list[Processor]

    def __init__(
        self,
        preprocessors: list[ProcessorSettings] | None = None,
        postprocessors: list[ProcessorSettings] | None = None,
    ) -> None:
        self.preprocessors = (
            [
                processor_cls(processor_config)  # pyright: ignore[reportCallIssue]
                for processor_config in preprocessors
                if (processor_cls := PROCESSOR_CLASSES[processor_config.kind])
                is not None
                and processor_config.enabled
            ]
            if preprocessors
            else []
        )
        self.postprocessors = (
            [
                processor_cls(processor_config)  # pyright: ignore[reportCallIssue]
                for processor_config in postprocessors
                if (processor_cls := PROCESSOR_CLASSES[processor_config.kind])
                is not None
                and processor_config.enabled
            ]
            if postprocessors
            else []
        )

    def preprocess(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
    ) -> TranslationContext:
        ctx = TranslationContext(
            phase="pre",
            source_text=text,
            preprocessed_text="",
            translated_text="",
            postprocessed_text="",
            text=text,
            source_lang=source_lang,
            target_lang=target_lang,
        )
        for processor in self.preprocessors:
            ctx = processor.process(replace(ctx))
        return replace(ctx, preprocessed_text=ctx.text)

    def postprocess(
        self,
        ctx: TranslationContext,
        text: str,
    ) -> TranslationContext:
        ctx = replace(ctx, phase="post", translated_text=text, text=text)
        for processor in self.postprocessors:
            ctx = processor.process(replace(ctx))
        return replace(ctx, postprocessed_text=ctx.text)
