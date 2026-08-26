import re

from tlserver.config import GlossaryProcessorSettings
from tlserver.processor import TranslationContext

# TODO: whole-word matching
# TODO: language-specific entries?
# TODO: inflections?
# TODO: priority?


class GlossaryProcessor:
    glossary: list[tuple[str, str, str, re.Pattern[str] | None]]
    _preprocess_glossary: list[tuple[str, str, str, re.Pattern[str] | None]]

    def __init__(self, config: GlossaryProcessorSettings) -> None:
        # TODO: move validation for duplicate/conflicting entries into config loading
        # TODO: let one glossary configuration run in both phases without duplicating
        # it in the preprocessor and postprocessor settings
        self.glossary = [
            (
                entry.source,
                f"__TLSERVER_GLOSSARY_{index}__",
                entry.target,
                (
                    None
                    if entry.case_sensitive
                    else re.compile(re.escape(entry.source), re.IGNORECASE)
                ),
            )
            for index, entry in enumerate(config.glossary)
        ]

        if any(not source for source, *_ in self.glossary):
            raise ValueError("Glossary sources must not be empty")

        # replace longer entries first so something like "mayano top gun" is protected
        # before shorter, overlapping entries like "mayano"
        # TODO: use one combined matching pass so later entries cannot match text
        # inserted as a placeholder by an earlier entry
        self._preprocess_glossary = sorted(
            self.glossary,
            key=lambda entry: len(entry[0]),
            reverse=True,
        )

    def process(self, ctx: TranslationContext) -> TranslationContext:
        if ctx.phase == "pre":
            # TODO: store a per-request token map in ctx.metadata
            # TODO: use tokens that better survive backend case/whitespace changes
            for source, placeholder, _, pattern in self._preprocess_glossary:
                if pattern is None:
                    ctx.text = ctx.text.replace(source, placeholder)
                else:
                    ctx.text = pattern.sub(placeholder, ctx.text)
        else:
            # TODO: record or warn when a placeholder does not survive translation
            for _, placeholder, target, _ in self.glossary:
                ctx.text = ctx.text.replace(placeholder, target)

        return ctx
