from jinja2 import Environment, StrictUndefined, select_autoescape
from loguru import logger
from openai import AsyncOpenAI

from tlserver.config import LLMTranslatorSettings
from tlserver.pipeline import TranslationPipeline
from tlserver.processor import TranslationContext

template_environment = Environment(
    autoescape=select_autoescape(default_for_string=False),
    undefined=StrictUndefined,
)


class LLMTranslator:
    def __init__(self, config: LLMTranslatorSettings) -> None:
        self.config = config
        self.translator_ready_or_not = False
        self.can_change_language_or_not = True
        self.messages = []
        self.translator = ""
        self.stop_translation = False

        self.client = AsyncOpenAI(
            api_key=config.api_key.get_secret_value(),
            base_url=str(config.api_server) if config.is_local else None,
        )

        self.pipeline = TranslationPipeline(config.preprocessors, config.postprocessors)

        self.system_prompt = ""
        self.system_prompt_template = template_environment.from_string(
            self.config.system_prompt
        )
        self.message_template = template_environment.from_string(
            self.config.message_template
        )

        self._process_system_prompt()

    def _process_system_prompt(self) -> None:
        self.messages = []
        self.system_prompt = self.system_prompt_template.render(
            input_language=self.config.input_language,
            output_language=self.config.output_language,
        )
        self.messages.append({"role": "system", "content": self.system_prompt})

    def _construct_message(self, ctx: TranslationContext) -> dict[str, str]:
        message = self.message_template.render(
            text=ctx.text,
        )
        return {"role": "user", "content": message}

    @property
    def is_ready(self) -> bool:
        return self.translator_ready_or_not

    def pause(self) -> None:
        self.stop_translation = True

    def resume(self) -> None:
        self.stop_translation = False

    def activate(self) -> bool:
        self.translator_ready_or_not = True
        return self.translator_ready_or_not

    async def close(self) -> None:
        await self.client.close()

    async def execute(self) -> str:
        request: dict[str, object] = {
            "model": self.config.model_name,
            "messages": self.messages,
        }

        for name in (
            "temperature",
            "top_p",
            "presence_penalty",
            "frequency_penalty",
        ):
            value = getattr(self.config, name)
            if value is not None:
                request[name] = value

        extra_body = {
            name: value
            for name in ("top_k", "min_p", "repeat_penalty")
            if (value := getattr(self.config, name)) is not None
        }
        if extra_body:
            request["extra_body"] = extra_body

        response = await self.client.chat.completions.create(**request)  # pyright: ignore[reportArgumentType]

        logger.debug("messages: {}", self.messages)

        content = response.choices[0].message.content
        if content is None:
            msg = "The language model returned no text"
            raise ValueError(msg)
        return content

    async def _translate(self, message: str) -> str:
        ctx = self.pipeline.preprocess(
            message,
            self.config.input_language,
            self.config.output_language,
        )
        if self.stop_translation:
            return "Translation is paused at the moment"
        self.messages.append(self._construct_message(ctx))
        result = await self.execute()
        self.messages.append({"role": "assistant", "content": result})
        # Ensure only the last 10 user and assistant messages are kept
        # 10 user/assistant messages + 1 system message
        if len(self.messages) > self.config.context_lines:
            self.messages = [
                self.messages[0],
                *self.messages[-self.config.context_lines :],
            ]
        ctx = self.pipeline.postprocess(ctx, result)
        return ctx.text

    async def translate(self, message: str) -> str:
        result = await self._translate(message)
        logger.info(f"{message!r}   ->   {result!r}")
        return result

    async def translate_batch(self, list_of_text_input: list[str]) -> list[str]:
        if self.stop_translation:
            return ["Translation is paused at the moment"]
        translation_list = []
        for text_input in list_of_text_input:
            translation = await self._translate(text_input)
            translation_list.append(translation)
        for original, translated in zip(
            list_of_text_input, translation_list, strict=True
        ):
            logger.info(f"{original!r}   ->   {translated!r}")
        return translation_list

    def check_if_language_available(self, language: str) -> bool:
        return self.config.supported_languages.get(language) is not None

    def change_output_language(self, output_language: str) -> str:
        if self.can_change_language_or_not:
            if self.check_if_language_available(output_language):
                self.config.output_language = output_language
                # Replace the system message in the messages list
                self._process_system_prompt()
                return f"output language changed to {output_language}"
            return "sorry, translator doesn't have this language"
        return "sorry, this translator can't change languages"

    def change_input_language(self, input_language: str) -> str:
        if self.can_change_language_or_not:
            if self.check_if_language_available(input_language):
                self.config.input_language = input_language
                # Replace the system message in the messages list
                self._process_system_prompt()
                return f"input language changed to {input_language}"
            return "sorry, translator doesn't have this language"
        return "sorry, this translator can't change languages"
