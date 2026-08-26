import re

from tlserver.config import RegexProcessorSettings
from tlserver.processor import TranslationContext


class RegexProcessor:
    pattern: re.Pattern[str]
    replacement: str

    def __init__(self, config: RegexProcessorSettings) -> None:
        self.pattern = re.compile(config.pattern)
        self.replacement = config.replacement

    def process(self, ctx: TranslationContext) -> TranslationContext:
        ctx.text = self.pattern.sub(self.replacement, ctx.text)
        return ctx
