from functools import partial

import ctranslate2
import sentencepiece as spm
import trio
from loguru import logger

from tlserver import plugins
from tlserver.config import OfflineTranslatorSettings


def tokenize_batch(text: list[str] | str, sp_source_model: str) -> list[list[str]]:
    sp = spm.SentencePieceProcessor(sp_source_model)  # pyright: ignore[reportCallIssue]
    if isinstance(text, list):
        return sp.encode(text, out_type=str)  # pyright: ignore[reportAttributeAccessIssue]
    return [sp.encode(text, out_type=str)]  # pyright: ignore[reportAttributeAccessIssue]


def detokenize_batch(text: list[list[str]], sp_target_model: str) -> list[str]:
    sp = spm.SentencePieceProcessor(sp_target_model)  # pyright: ignore[reportCallIssue]
    return sp.decode(text)  # pyright: ignore[reportAttributeAccessIssue]


class OfflineTranslator:
    def __init__(self, config: OfflineTranslatorSettings) -> None:
        self.config = config
        self.translator_ready_or_not = False
        self.can_change_language_or_not = False
        self.translator: ctranslate2.Translator | None = None
        self.stop_translation = False

    @property
    def is_ready(self) -> bool:
        return self.translator_ready_or_not

    def pause(self) -> None:
        self.stop_translation = True

    def resume(self) -> None:
        self.stop_translation = False

    def activate(self) -> bool:
        self.translator = ctranslate2.Translator(
            str(self.config.translate_model_path),
            device=self.config.device,
            intra_threads=self.config.intra_threads,
            inter_threads=self.config.inter_threads,
        )
        self.translator_ready_or_not = True
        return self.translator_ready_or_not

    async def translate(self, message: str) -> str:
        if self.stop_translation:
            return "Translation is paused at the moment"

        message = plugins.process_input_text(message)

        translated = await trio.to_thread.run_sync(
            partial(
                self.translator.translate_batch,  # pyright: ignore[reportOptionalMemberAccess]
                source=tokenize_batch(message, str(self.config.tok_source_model_path)),
                beam_size=self.config.beam_size,
                num_hypotheses=1,
                return_alternatives=False,
                disable_unk=self.config.disable_unk,
                replace_unknowns=False,
                repetition_penalty=self.config.repetition_penalty,
            )
        )

        final_result = []
        for result in translated:
            detokenized = "".join(
                detokenize_batch(
                    result.hypotheses[0], str(self.config.tok_target_model_path)
                )
            )
            final_result.append(detokenized)

        result = plugins.process_output_text(final_result[0])
        logger.info(f"{message!r}   ->   {translated!r}")
        return result

    async def translate_batch(self, list_of_text_input: list[str]) -> list[str]:
        if self.stop_translation:
            return ["Translation is paused at the moment"]
        translated = await trio.to_thread.run_sync(
            partial(
                self.translator.translate_batch,  # pyright: ignore[reportOptionalMemberAccess]
                source=tokenize_batch(
                    list_of_text_input, str(self.config.tok_source_model_path)
                ),
                beam_size=self.config.beam_size,
                num_hypotheses=1,
                return_alternatives=False,
                disable_unk=self.config.disable_unk,
                replace_unknowns=False,
                repetition_penalty=self.config.repetition_penalty,
            )
        )

        final_result = []
        for result in translated:
            detokenized = "".join(
                detokenize_batch(
                    result.hypotheses[0], str(self.config.tok_target_model_path)
                )
            )
            final_result.append(detokenized)
        for original, translated in zip(list_of_text_input, final_result, strict=True):
            logger.info(f"{original!r}   ->   {translated!r}")
        return final_result

    def check_if_language_available(self, language: str) -> bool:
        return self.config.supported_languages.get(language) is not None

    def change_output_language(self, output_language: str) -> str:
        if self.can_change_language_or_not:
            if self.check_if_language_available(output_language):
                self.config.output_language = output_language
                return f"output language changed to {output_language}"
            return "sorry, translator doesn't have this language"
        return "sorry, this translator can't change languages"

    def change_input_language(self, input_language: str) -> str:
        if self.can_change_language_or_not:
            if self.check_if_language_available(input_language):
                self.config.input_language = input_language
                return f"input language changed to {input_language}"
            return "sorry, translator doesn't have this language"
        return "sorry, this translator can't change languages"
