from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import pytest
from pydantic import ValidationError
from quart import Quart

import tlserver.handler as handler_module
from tlserver.config import LLMTranslatorSettings
from tlserver.handler import (
    Command,
    CommandPayload,
    LegacyTranslatorHandler,
    legacy_dispatcher,
)


@dataclass
class FakeTranslator:
    config: LLMTranslatorSettings = field(
        default_factory=lambda: LLMTranslatorSettings(kind="LLM", port=19001)
    )
    is_ready: bool = True
    calls: list[tuple[str, Any]] = field(default_factory=list)

    def activate(self) -> bool:
        self.calls.append(("activate", None))
        return True

    def pause(self) -> str:
        self.calls.append(("pause", None))
        return "paused"

    def resume(self) -> str:
        self.calls.append(("resume", None))
        return "resumed"

    async def translate(self, value: str) -> str:
        self.calls.append(("translate", value))
        return f"one:{value}"

    async def translate_batch(self, value: list[str]) -> list[str]:
        self.calls.append(("translate_batch", value))
        return [f"many:{item}" for item in value]

    def change_input_language(self, value: str) -> str:
        self.calls.append(("input", value))
        return f"input:{value}"

    def change_output_language(self, value: str) -> str:
        self.calls.append(("output", value))
        return f"output:{value}"


class FakeRequest:
    def __init__(self, payload: dict[str, Any]) -> None:
        self.payload = payload

    async def get_json(self, *, force: bool) -> dict[str, Any]:
        assert force is True
        return self.payload


@pytest.mark.parametrize(
    ("payload", "expected", "call"),
    [
        ({"message": "close server"}, None, None),
        ({"message": "check if server is ready"}, True, None),
        (
            {"message": "translate sentences", "content": "hello"},
            "one:hello",
            ("translate", "hello"),
        ),
        (
            {"message": "translate sentences", "content": ["a", "b"]},
            ["many:a", "many:b"],
            ("translate_batch", ["a", "b"]),
        ),
        (
            {"message": "change input language", "content": "English"},
            "input:English",
            ("input", "English"),
        ),
        (
            {"message": "change output language", "content": "French"},
            "output:French",
            ("output", "French"),
        ),
        ({"message": "pause"}, "paused", ("pause", None)),
        ({"message": "resume"}, "resumed", ("resume", None)),
    ],
)
def test_legacy_handler_dispatches_every_command(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, Any],
    expected: Any,
    call: tuple[str, Any] | None,
) -> None:
    translator = FakeTranslator()
    legacy_handler = LegacyTranslatorHandler(translator)  # pyright: ignore[reportArgumentType]
    monkeypatch.setattr(handler_module.quart.json, "jsonify", lambda value: value)

    result = asyncio.run(legacy_handler.receive_command(FakeRequest(payload)))  # pyright: ignore[reportArgumentType]

    assert result == expected
    assert translator.calls[0] == ("activate", None)
    if call is not None:
        assert translator.calls[-1] == call


def test_command_payload_validates_content_and_normalizes_legacy_batches() -> None:
    payload = CommandPayload(message=Command.TRANSLATE_SENTENCES, content=["a"])

    assert payload.message is Command.TRANSLATE_BATCH
    assert payload.content == ["a"]
    with pytest.raises(ValidationError, match="must not provide content"):
        CommandPayload(message=Command.READY, content="unexpected")
    with pytest.raises(ValidationError):
        CommandPayload(message=Command.TRANSLATE_BATCH, content="not a list")


def test_legacy_handler_requires_a_port() -> None:
    translator = FakeTranslator(
        config=LLMTranslatorSettings(kind="LLM", port=None, path="/modern")
    )

    with pytest.raises(ValueError, match="requires a port"):
        LegacyTranslatorHandler(translator)  # pyright: ignore[reportArgumentType]


def test_legacy_dispatcher_routes_by_request_port() -> None:
    first = LegacyTranslatorHandler(FakeTranslator())  # pyright: ignore[reportArgumentType]
    blueprint, ports = legacy_dispatcher([first])
    app = Quart(__name__)
    app.register_blueprint(blueprint)

    async def dispatch(port: int | None) -> tuple[int, str]:
        async with app.test_request_context(
            "/", method="POST", json={"message": "check if server is ready"}
        ):
            if port is None:
                handler_module.request.scope["server"] = None
            else:
                handler_module.request.scope["server"] = ("127.0.0.1", port)
            response = await app.view_functions["legacy.legacy_dispatch"]()
            return response.status_code, await response.get_data(as_text=True)

    assert ports == {19001}
    assert asyncio.run(dispatch(19001)) == (200, "true\n")
    assert asyncio.run(dispatch(19999)) == (404, "No plugin for port 19999\n")
    assert asyncio.run(dispatch(None)) == (404, "Unable to determine request port\n")
