from __future__ import annotations

import os
import sys
import tomllib
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    Protocol,
    Self,
    TypeGuard,
    overload,
)

from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    DirectoryPath,
    Field,
    FilePath,
    GetCoreSchemaHandler,
    HttpUrl,
    SecretStr,
    ValidationInfo,
    model_validator,
)
from pydantic_core import core_schema
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

if TYPE_CHECKING:
    from pydantic.fields import FieldInfo


class HasPort(Protocol):
    port: int


class HasPath(Protocol):
    path: str


class Version(Enum):
    LEGACY = 0
    V1 = 1

    @overload
    def applies(
        self: Literal[Version.LEGACY], config: TranslatorSettingsBase
    ) -> TypeGuard[HasPort]: ...
    @overload
    def applies(
        self: Literal[Version.V1], config: TranslatorSettingsBase
    ) -> TypeGuard[HasPath]: ...
    @overload
    def applies(self: Version, config: TranslatorSettingsBase) -> bool: ...

    def applies(self, config: TranslatorSettingsBase) -> bool:
        if self is Version.LEGACY:
            return config.port is not None
        if self is Version.V1:
            return config.path is not None
        return False


class Conditional:
    def __init__(self, gate_field: str) -> None:
        self.gate_field = gate_field

    def __get_pydantic_core_schema__(
        self,
        source: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validator(
            value: Any,  # noqa: ANN401
            validator: core_schema.ValidatorFunctionWrapHandler,
            info: ValidationInfo,
        ) -> Any:  # noqa: ANN401
            if info.data.get(self.gate_field, True):
                return validator(value)
            return value

        return core_schema.with_info_wrap_validator_function(validator, handler(source))


class _BaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
    )


class ProcessorSettingsBase(_BaseModel):
    enabled: bool = True


class NormalizeProcessorSettings(ProcessorSettingsBase):
    kind: Literal["normalize"]
    unicode_form: Literal["NFC", "NFD", "NFKC", "NFKD"] = "NFC"
    normalize_newlines: bool = True


class ReplaceProcessorSettings(ProcessorSettingsBase):
    kind: Literal["replace"]
    replacements: dict[str, str]


class RegexProcessorSettings(ProcessorSettingsBase):
    kind: Literal["regex_replace"]
    pattern: str
    replacement: str


@dataclass
class GlossaryEntry:
    source: str
    target: str
    case_sensitive: bool = True


class GlossaryProcessorSettings(ProcessorSettingsBase):
    kind: Literal["glossary"]
    glossary: list[GlossaryEntry]


# TODO: this...
class PlaceholderProcessorSettings(ProcessorSettingsBase):
    kind: Literal["placeholder"]


ProcessorSettings = Annotated[
    NormalizeProcessorSettings
    | ReplaceProcessorSettings
    | RegexProcessorSettings
    | GlossaryProcessorSettings
    | PlaceholderProcessorSettings,
    Field(discriminator="kind"),
]


class TranslatorSettingsBase(_BaseModel):
    enabled: bool = True
    port: int | None = None
    path: str | None = None

    input_language: str = "Japanese"
    output_language: str = "English"
    supported_languages: dict[str, str]

    preprocessors: list[ProcessorSettings] = Field(default_factory=list)
    postprocessors: list[ProcessorSettings] = Field(default_factory=list)

    @model_validator(mode="after")
    def at_least_one(self) -> Self:
        if not self.enabled:
            return self
        fields = ["port", "path"]
        set_fields = [
            field for field in fields if getattr(self, field, None) is not None
        ]
        if len(set_fields) < 1:
            expect = " or ".join(fields)
            raise ValueError(f"At least one of {expect} must be provided.")
        return self


class OfflineTranslatorSettings(TranslatorSettingsBase):
    kind: Literal["Offline"]
    supported_languages: dict[str, str] = Field(
        default_factory=lambda: {
            "English": "English",
            "Japanese": "Japanese",
        }
    )
    port: int | None = 14366
    initial_phrase: str = "お疲れさまでした"
    gpu: bool = False
    device: str = "cpu"
    intra_threads: int = 0
    inter_threads: int = 4
    beam_size: int = 5
    repetition_penalty: int = 3
    silent: bool = False
    disable_unk: bool = True

    translate_model_path: Annotated[DirectoryPath, Conditional("enabled")] = Path(
        "./assets/models/translate/"
    )
    tok_source_model_path: Annotated[FilePath, Conditional("enabled")] = Path(
        "./assets/models/tokenise/spm.ja.nopretok.model"
    )
    tok_target_model_path: Annotated[FilePath, Conditional("enabled")] = Path(
        "./assets/models/tokenise/spm.en.nopretok.model"
    )


class GoogleTranslatorSettings(TranslatorSettingsBase):
    kind: Literal["Google"]
    supported_languages: dict[str, str] = Field(
        default_factory=lambda: {
            "English": "en",
            "Chinese": "zh-CN",
            "Japanese": "ja",
            "Korean": "ko",
            "Spanish": "es",
            "French": "fr",
            "Portuguese": "pt",
            "Vietnamese": "vi",
            "Indonesian": "id",
            "Arabic": "ar",
            "Thai": "th",
            "Turkish": "tr",
        }
    )
    port: int | None = 14367


class LLMTranslatorSettings(TranslatorSettingsBase):
    kind: Literal["LLM"]
    supported_languages: dict[str, str] = Field(
        default_factory=lambda: {
            "English": "English",
            "Chinese": "Simplified Chinese",
            "Japanese": "Japanese",
            "Korean": "Korean",
            "Spanish": "Spanish",
            "Portuguese": "Brazilian Portuguese",
            "Vietnamese": "Vietnamese",
            "Indonesian": "Indonesian",
            "Arabic": "Arabic",
            "German": "German",
        }
    )
    port: int | None = 14368
    is_local: bool = True
    model_name: str = "sugoi14b"
    api_server: HttpUrl = HttpUrl("http://127.0.0.1:1234/v1")
    api_key: SecretStr = SecretStr("sk-fakefakefake")
    system_prompt: str = (
        "You are a professional translator whose primary goal is to "
        "precisely translate {{ input_language }} to {{ output_language }}. "
        "You can speak colloquially if it makes the translation more accurate. "
        "Only respond in {{ output_language }}. "
        "If you are unsure of a {{ input_language }} sentence, "
        "still always try your best estimate to respond with "
        "a complete {{ output_language }} translation."
    )
    message_template: str = "{{ text }}"
    context_lines: int = 50
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    min_p: float | None = None
    repeat_penalty: float | None = None
    presence_penalty: float | None = None
    frequency_penalty: float | None = None


class DeepLTranslatorSettings(TranslatorSettingsBase):
    kind: Literal["DeepL"]
    supported_languages: dict[str, str] = Field(
        default_factory=lambda: {
            "English": "en-us",
            "Chinese": "zh",
            "Japanese": "ja",
            "Korean": "ko",
            "Spanish": "es",
            "French": "fr",
            "Portuguese": "pt-br",
            "Indonesian": "id",
            "Arabic": "ar",
            "Turkish": "tr",
        }
    )
    port: int | None = 14369
    hide_browser_window: bool = True
    default_navigation_timeout: int = 30000
    website_url: HttpUrl = HttpUrl("https://www.deepl.com/en/translator#")
    language_separator: str = "/"
    input_text_separator: str = "/"
    input_textbox_id: str = "[data-testid=translator-source-input]"
    result_textbox_id: str = "[data-testid=translator-target-input]"
    initial_phrase: str = "Deepl"


TranslatorSettings = Annotated[
    OfflineTranslatorSettings
    | GoogleTranslatorSettings
    | DeepLTranslatorSettings
    | LLMTranslatorSettings,
    Field(discriminator="kind"),
]


class AppSettings(BaseSettings):
    debug: bool = False

    # no effect on legacy handlers
    root_port: int

    translators: list[TranslatorSettings] = Field(default_factory=list)

    # -----

    model_config = SettingsConfigDict(
        env_prefix="TLSERVER_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="forbid",
        validate_default=True,
        validate_assignment=True,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            TOMLConfigSettingsSource(settings_cls),
            file_secret_settings,
        )

    @model_validator(mode="after")
    def ensure_unique_handler_mapping(self) -> Self:
        active_tls = [t for t in self.translators if t.enabled]

        ports = Counter(
            [t.port for t in active_tls if t.port is not None] + [self.root_port]
        )
        duplicates = {p for p, c in ports.items() if c > 1}
        if duplicates:
            raise ValueError(f"Duplicate plugin ports detected: {sorted(duplicates)}")

        paths = Counter([t.path for t in active_tls if t.path is not None])
        duplicates = {p for p, c in paths.items() if c > 1}
        if duplicates:
            raise ValueError(f"Duplicate plugin paths detected: {sorted(duplicates)}")
        return self


def get_executable_dir() -> Path | None:
    executable_path = None
    if not executable_path and getattr(sys, "frozen", False):
        executable_path = Path(sys.executable).resolve().parent
        logger.debug("frozen executable, executable at {}", executable_path)
    # i think this one is scuffed
    if not executable_path and hasattr(sys.modules.get("__main__"), "__file__"):
        executable_path = Path(sys.modules["__main__"].__file__).resolve().parent  # pyright: ignore[reportArgumentType]
        logger.debug("__main__, executable at {}", executable_path)
    return executable_path


def find_config_path() -> Path | None:
    candidates: list[tuple[str, Path]] = []
    if env := os.getenv("TLSERVER_CONFIG_PATH"):
        candidates.append(("env TLSERVER_CONFIG_PATH", Path(env).expanduser()))
    if xdg := os.getenv("XDG_CONFIG_HOME"):
        candidates.append(("xdg config home", Path(xdg) / "tlserver" / "config.toml"))
    if appdt := os.getenv("APPDATA"):
        candidates.append(("appdata", Path(appdt) / "tlserver" / "config.toml"))
    candidates.append(("cwd", Path.cwd() / "config.toml"))

    for label, p in candidates:
        logger.debug("resolving {} -> {}", label, p)
        try:
            if p.is_file():
                logger.debug("config at {}", p)
                return p
        except OSError:
            logger.debug("invalid path for {}: {}", label, p)

    return None


class TOMLConfigSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self,
        field: FieldInfo,  # noqa: ARG002
        field_name: str,
    ) -> tuple[Any, str, bool]:
        field_value = self.file_dict.get(field_name)
        return field_value, field_name, False

    def prepare_field_value(
        self,
        field_name: str,  # noqa: ARG002
        field: FieldInfo,  # noqa: ARG002
        value: Any,  # noqa: ANN401
        value_is_complex: bool,  # noqa: ARG002, FBT001
    ) -> Any:  # noqa: ANN401
        return value

    def __call__(self) -> dict[str, Any]:
        result: dict[str, Any] = {}

        file_path = find_config_path()

        encoding = self.config.get("env_file_encoding")
        if file_path and file_path.is_file():
            self.file_dict = tomllib.loads(file_path.read_text(encoding))
        else:
            return result

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                result[field_key] = field_value

        return result
