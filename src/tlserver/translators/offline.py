from functools import partial

import ctranslate2  # pyright: ignore[reportMissingTypeStubs]
import sentencepiece as spm
import trio
from loguru import logger

from tlserver.config import OfflineTranslatorSettings
from tlserver.pipeline import TranslationPipeline


def tokenize_batch(text: list[str] | str, sp_source_model: str) -> list[list[str]]:
    sp = spm.SentencePieceProcessor(sp_source_model)
    if isinstance(text, list):
        return sp.encode(text, out_type=str)  # pyright: ignore[reportAny]
    return [sp.encode(text, out_type=str)]


def detokenize_batch(text: list[list[str]], sp_target_model: str) -> list[str]:
    sp = spm.SentencePieceProcessor(sp_target_model)
    return sp.decode(text)  # pyright: ignore[reportAny]


class OfflineTranslator:
    def __init__(self, config: OfflineTranslatorSettings) -> None:
        self.config = config
        self.translator_ready_or_not = False
        self.can_change_language_or_not = False
        self.translator: ctranslate2.Translator | None = None
        self.stop_translation = False

        self.pipeline = TranslationPipeline(config.preprocessors, config.postprocessors)

    @property
    def is_ready(self) -> bool:
        return self.translator_ready_or_not

    def pause(self) -> None:
        self.stop_translation = True

    def resume(self) -> None:
        self.stop_translation = False

    def activate(self) -> bool:
        self.translator = ctranslate2.Translator(  # pyright: ignore[reportUnknownMemberType]
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

        ctx = self.pipeline.preprocess(
            message,
            self.config.input_language,
            self.config.output_language,
        )

        translated = await trio.to_thread.run_sync(  # pyright: ignore[reportUnknownVariableType]
            partial(  # pyright: ignore[reportUnknownArgumentType]
                self.translator.translate_batch,  # pyright: ignore[reportUnknownMemberType, reportOptionalMemberAccess]
                source=tokenize_batch(ctx.text, str(self.config.tok_source_model_path)),
                beam_size=self.config.beam_size,
                num_hypotheses=1,
                return_alternatives=False,
                disable_unk=self.config.disable_unk,
                replace_unknowns=False,
                repetition_penalty=self.config.repetition_penalty,
            )
        )
        translated = translated[0]  # pyright: ignore[reportUnknownVariableType]

        detokenized = "".join(
            detokenize_batch(
                translated.hypotheses[0],  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
                str(self.config.tok_target_model_path),
            )
        )

        ctx = self.pipeline.postprocess(ctx, detokenized)

        logger.info(f"{ctx.source_text!r}   ->   {ctx.text!r}")
        return ctx.text

    async def translate_batch(self, list_of_text_input: list[str]) -> list[str]:
        if self.stop_translation:
            return ["Translation is paused at the moment"]

        ctxs = [
            self.pipeline.preprocess(
                message,
                self.config.input_language,
                self.config.output_language,
            )
            for message in list_of_text_input
        ]

        translated = await trio.to_thread.run_sync(  # pyright: ignore[reportUnknownVariableType]
            partial(  # pyright: ignore[reportUnknownArgumentType]
                self.translator.translate_batch,  # pyright: ignore[reportUnknownMemberType, reportOptionalMemberAccess]
                source=tokenize_batch(
                    [ctx.text for ctx in ctxs], str(self.config.tok_source_model_path)
                ),
                beam_size=self.config.beam_size,
                num_hypotheses=1,
                return_alternatives=False,
                disable_unk=self.config.disable_unk,
                replace_unknowns=False,
                repetition_penalty=self.config.repetition_penalty,
            )
        )

        detokenized = [
            "".join(
                detokenize_batch(
                    result.hypotheses[0],  # pyright: ignore[reportUnknownMemberType]
                    str(self.config.tok_target_model_path),
                )
            )
            for result in translated  # pyright: ignore[reportUnknownVariableType]
        ]

        ctxs = [
            self.pipeline.postprocess(ctx, text)
            for ctx, text in zip(ctxs, detokenized, strict=True)
        ]

        for ctx in ctxs:
            logger.info(f"{ctx.source_text!r}   ->   {ctx.text!r}")
        return [ctx.text for ctx in ctxs]

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
