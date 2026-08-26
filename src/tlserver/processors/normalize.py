import unicodedata
from typing import Literal

from tlserver.config import NormalizeProcessorSettings
from tlserver.processor import TranslationContext


class NormalizeProcessor:
    unicode_form: Literal["NFC", "NFD", "NFKC", "NFKD"]
    normalize_newlines: bool

    def __init__(self, config: NormalizeProcessorSettings) -> None:
        self.unicode_form = config.unicode_form
        self.normalize_newlines = config.normalize_newlines

    def process(self, ctx: TranslationContext) -> TranslationContext:
        ctx.text = unicodedata.normalize(self.unicode_form, ctx.text)

        if self.normalize_newlines:
            ctx.text = ctx.text.replace("\r\n", "\n").replace("\r", "\n")

        return ctx
