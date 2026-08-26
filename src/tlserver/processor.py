from dataclasses import dataclass, field
from typing import Any, Literal, Protocol


@dataclass
class TranslationContext:
    source_text: str
    preprocessed_text: str
    translated_text: str
    postprocessed_text: str
    text: str

    phase: Literal["pre", "post"]

    source_lang: str
    target_lang: str

    metadata: dict[str, Any] = field(default_factory=dict)


class Processor(Protocol):
    def process(
        self,
        ctx: TranslationContext,
    ) -> TranslationContext: ...
