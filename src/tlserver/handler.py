import uuid
from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from enum import StrEnum
from time import monotonic
from typing import Any, ClassVar, Self

import quart
from loguru import logger
from pydantic import BaseModel, TypeAdapter, model_validator
from quart import Blueprint, Request, Response, request

from tlserver.config import Version
from tlserver.translator import Translator


@contextmanager
def timed(action: str) -> Generator[None, Any, None]:
    tick = monotonic()
    try:
        yield
    finally:
        tock = monotonic()
        logger.info(f"{action} in {tock - tick:.3f}s")


class Command(StrEnum):
    CLOSE = "close server"
    READY = "check if server is ready"
    TRANSLATE_SENTENCES = "translate sentences"
    TRANSLATE_BATCH = "translate batch"
    CHANGE_INPUT = "change input language"
    CHANGE_OUTPUT = "change output language"
    PAUSE = "pause"
    RESUME = "resume"


class CommandPayload(BaseModel):
    message: Command
    content: Any = None

    _content_adapters: ClassVar[dict[Command, TypeAdapter[Any]]] = {
        Command.TRANSLATE_SENTENCES: TypeAdapter(str),
        Command.TRANSLATE_BATCH: TypeAdapter(list[str]),
        Command.CHANGE_INPUT: TypeAdapter(str),
        Command.CHANGE_OUTPUT: TypeAdapter(str),
    }

    @model_validator(mode="after")
    def normalize_legacy_translate(self) -> Self:
        # special case for legacy support
        if self.message is Command.TRANSLATE_SENTENCES and isinstance(
            self.content, list
        ):
            logger.debug(
                "legacy support: translate single sentence converted to batch translate"
            )
            self.message = Command.TRANSLATE_BATCH
        return self

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        adapter = self._content_adapters.get(self.message)
        if adapter is None:
            if self.content not in (None, {}):
                raise ValueError(f"`{self.message}` must not provide content")
        else:
            self.content = adapter.validate_python(self.content)
        return self


class TranslatorHandler(ABC):
    translator: Translator

    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def receive_command(self, request: Request) -> Response:
        pass


class LegacyTranslatorHandler(TranslatorHandler):
    def __init__(self, translator: Translator) -> None:
        config = translator.config
        if not Version.LEGACY.applies(config):
            raise ValueError("Legacy translator requires a port")
        self.port = config.port
        self.translator = translator
        self.translator.activate()

    async def receive_command(self, request: Request) -> Response:
        with logger.contextualize(uid=uuid.uuid4()), timed("command handled") as _:
            payload = CommandPayload.model_validate(await request.get_json(force=True))

            logger.info(f"received command {payload}")

            response = None

            match payload.message:
                case Command.CLOSE:
                    # TODO: implement "ending the handler" rather than the server
                    # we'd like to stop handling the port too if possible
                    # (how do we stop only one app?)
                    # for now we ignore this
                    logger.debug("die command ignored")

                case Command.READY:
                    response = self.translator.is_ready

                case Command.TRANSLATE_SENTENCES:
                    with timed("translated") as _:
                        translation = await self.translator.translate(payload.content)
                    response = translation

                case Command.TRANSLATE_BATCH:
                    with timed("batch translated") as _:
                        translation = await self.translator.translate_batch(
                            payload.content
                        )
                    response = translation

                case Command.CHANGE_INPUT:
                    response = self.translator.change_input_language(payload.content)

                case Command.CHANGE_OUTPUT:
                    response = self.translator.change_output_language(payload.content)

                case Command.PAUSE:
                    response = self.translator.pause()

                case Command.RESUME:
                    response = self.translator.resume()

            logger.info("response: {}", response)

            return quart.json.jsonify(response)


def legacy_dispatcher(
    handlers: Sequence[LegacyTranslatorHandler],
) -> tuple[Blueprint, set[int]]:
    _handlers = {}
    for handler in handlers:
        _handlers[handler.port] = handler

    legacy_bp = Blueprint("legacy", __name__)

    @legacy_bp.route("/", methods=["POST", "GET"])
    async def legacy_dispatch() -> Response:
        match request.scope.get("server"):
            case (_, int(port)):
                if handler := _handlers.get(port):
                    return await handler.receive_command(request)
                return Response(
                    f"No plugin for port {port}\n", status=404, mimetype="text/plain"
                )
            case _:
                return Response(
                    "Unable to determine request port\n",
                    status=404,
                    mimetype="text/plain",
                )

    return (legacy_bp, set(_handlers.keys()))


# TODO: modern v1 handler that uses paths and actually has a sane api
