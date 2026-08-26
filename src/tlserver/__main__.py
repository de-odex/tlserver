import inspect
import logging
import signal
import sys
from collections.abc import Sequence
from io import StringIO
from typing import Literal, overload

import trio
from hypercorn.config import Config
from hypercorn.trio import serve
from loguru import logger
from pydantic import ValidationError
from quart_cors import cors
from quart_trio import QuartTrio
from rich.console import Console
from rich.pretty import Pretty

from tlserver.config import AppSettings, Version
from tlserver.handler import (
    LegacyTranslatorHandler,
    TranslatorHandler,
    legacy_dispatcher,
)
from tlserver.translator import Translator
from tlserver.translators.llm import LLMTranslator
from tlserver.translators.offline import OfflineTranslator


def rich_str(obj: object) -> str:
    buf = StringIO()
    console = Console(file=buf, force_terminal=True, color_system="truecolor")
    console.print(Pretty(obj))
    return buf.getvalue().rstrip()


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen = "importlib" in filename and "_bootstrap" in filename
            if depth > 0 and not (is_logging or is_frozen):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


TRANSLATOR_CLASSES: dict[str, type[Translator] | None] = {
    "Offline": OfflineTranslator,
    "Google": None,
    "LLM": LLMTranslator,
    "DeepL": None,
}


def format_validation_error(exc: ValidationError) -> str:
    lines = ["Config validation failed:"]
    for err in exc.errors():
        location = " → ".join(str(part) for part in err["loc"])
        message = err["msg"]
        lines.append(f"- {location}: {message}")
    return "\n".join(lines)


config = None
try:
    # intentional ignore, we want config files to provide values
    config = AppSettings()  # pyright: ignore[reportCallIssue]
except ValidationError as exc:
    logger.error(format_validation_error(exc))
    sys.exit(1)
if not config.debug:
    logger.remove()
    logger.add(sys.stderr, level="INFO")
logger.info(f"Config loaded:\n{rich_str(config.model_dump())}")

app = QuartTrio(__name__)
app = cors(app, allow_origin="*")
die = trio.Event()

handlers: list[TranslatorHandler] = [
    LegacyTranslatorHandler(translator_cls(translator_config))  # pyright: ignore[reportCallIssue]
    for translator_config in config.translators
    if (translator_cls := TRANSLATOR_CLASSES[translator_config.kind]) is not None
    and translator_config.enabled
]


@app.before_serving
async def on_start() -> None:
    logger.info("Hello, starting up.")


@app.after_serving
async def on_stop() -> None:
    logger.info("Goodbye, shutting down.")


@overload
def versioned_handlers(
    handlers: list[TranslatorHandler], version: Literal[Version.LEGACY]
) -> Sequence[LegacyTranslatorHandler]: ...
@overload
def versioned_handlers(
    handlers: list[TranslatorHandler], version: Literal[Version.V1]
) -> Sequence[TranslatorHandler]: ...
def versioned_handlers(
    handlers: list[TranslatorHandler], version: Version
) -> Sequence[TranslatorHandler]:
    return [
        handler for handler in handlers if version.applies(handler.translator.config)
    ]


legacy_blueprint, ports = legacy_dispatcher(
    versioned_handlers(handlers, Version.LEGACY)
)

app.register_blueprint(legacy_blueprint)


async def amain() -> None:
    trio_token = trio.lowlevel.current_trio_token()

    def _handle_shutdown(signum: int, _frame: object) -> None:
        sig_name = signal.Signals(signum).name
        logger.info(f"Received {sig_name}; beginning graceful shutdown.")
        trio_token.run_sync_soon(die.set)

    for sig in (signal.SIGINT, signal.SIGTERM):
        if getattr(signal, sig.name, None) is not None:
            try:
                signal.signal(sig, _handle_shutdown)
            except ValueError as e:
                # SIGTERM is missing on Windows; ignore.
                logger.warning("Ignored error: {}", e)
                continue

    config = Config.from_mapping(
        bind=[f"0.0.0.0:{port}" for port in ports],
        errorlog=None,
    )

    logger.debug("hypercorn serving")
    try:
        await serve(
            app,
            config,
            shutdown_trigger=die.wait,
        )
    finally:
        logger.debug("hypercorn stopping")


def main() -> None:
    trio.run(amain)
