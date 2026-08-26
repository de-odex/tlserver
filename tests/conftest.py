from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from tlserver.processor import TranslationContext


def make_context(
    text: str,
    phase: str = "pre",
    *,
    source_text: str | None = None,
) -> TranslationContext:
    """Create a context with stable defaults for processor tests."""
    return TranslationContext(
        source_text=source_text if source_text is not None else text,
        preprocessed_text="",
        translated_text="",
        postprocessed_text="",
        text=text,
        phase=phase,  # pyright: ignore[reportArgumentType]
        source_lang="Japanese",
        target_lang="English",
    )


ValueT = TypeVar("ValueT")


async def run_sync_immediately(callback: Callable[[], ValueT]) -> ValueT:
    """Replacement for Trio's worker-thread helper in hermetic tests."""
    return callback()
