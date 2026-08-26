from tlserver.config import ReplaceProcessorSettings
from tlserver.processor import TranslationContext


class ReplaceProcessor:
    replacements: dict[str, str]

    def __init__(self, config: ReplaceProcessorSettings) -> None:
        self.replacements = config.replacements

    def process(self, ctx: TranslationContext) -> TranslationContext:
        for old, new in self.replacements.items():
            ctx.text = ctx.text.replace(old, new)

        return ctx
