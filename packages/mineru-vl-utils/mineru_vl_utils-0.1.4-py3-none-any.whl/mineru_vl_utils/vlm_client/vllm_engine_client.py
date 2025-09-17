import asyncio
from io import BytesIO
from typing import TYPE_CHECKING, List, Optional, Union

if TYPE_CHECKING:
    from vllm.outputs import RequestOutput
    from vllm.sampling_params import SamplingParams

from PIL import Image

from .base_client import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT,
    RequestError,
    ServerError,
    UnsupportedError,
    VlmClient,
)
from .utils import get_rgb_image, load_resource


class VllmEngineVlmClient(VlmClient):
    def __init__(
        self,
        vllm_llm,  # vllm.LLM instance
        prompt: str = DEFAULT_USER_PROMPT,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        temperature: float | None = None,
        top_p: float | None = None,
        top_k: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        repetition_penalty: float | None = None,
        no_repeat_ngram_size: int | None = None,  # not supported by vllm
        max_new_tokens: int | None = None,
        text_before_image: bool = False,
        allow_truncated_content: bool = False,
        batch_size: int = 0,
    ):
        super().__init__(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_new_tokens=max_new_tokens,
            text_before_image=text_before_image,
            allow_truncated_content=allow_truncated_content,
        )

        try:
            from vllm import LLM, SamplingParams
        except ImportError:
            raise ImportError("Please install vllm to use VllmEngineVlmClient.")

        if not vllm_llm:
            raise ValueError("vllm_llm is None.")
        if not isinstance(vllm_llm, LLM):
            raise ValueError("vllm_llm must be an instance of vllm.LLM.")

        self.vllm_llm = vllm_llm
        self.tokenizer = vllm_llm.get_tokenizer()
        self.model_max_length = vllm_llm.llm_engine.model_config.max_model_len
        self.VllmSamplingParams = SamplingParams
        self.batch_size = batch_size

    def build_messages(self, prompt: str) -> list[dict]:
        prompt = prompt or self.prompt
        messages = []
        if self.system_prompt:
            messages.append({"role": "system", "content": self.system_prompt})
        if "<image>" in prompt:
            prompt_1, prompt_2 = prompt.split("<image>", 1)
            user_messages = [
                *([{"type": "text", "text": prompt_1}] if prompt_1.strip() else []),
                {"type": "image"},
                *([{"type": "text", "text": prompt_2}] if prompt_2.strip() else []),
            ]
        elif self.text_before_image:
            user_messages = [
                {"type": "text", "text": prompt},
                {"type": "image"},
            ]
        else:  # image before text, which is the default behavior.
            user_messages = [
                {"type": "image"},
                {"type": "text", "text": prompt},
            ]
        messages.append({"role": "user", "content": user_messages})
        return messages

    def get_output_content(self, output: "RequestOutput") -> str:
        if not output.finished:
            raise ServerError("The output generation was not finished.")

        choices = output.outputs
        if not (isinstance(choices, list) and choices):
            raise ServerError("No choices found in the output.")

        finish_reason = choices[0].finish_reason
        if finish_reason == "length":
            if not self.allow_truncated_content:
                raise RequestError("The output was truncated due to length limit.")
            else:
                print("Warning: The output was truncated due to length limit.")
        elif finish_reason != "stop":
            raise RequestError(f"Unexpected finish reason: {finish_reason}")

        return choices[0].text

    def predict(
        self,
        image: str | bytes | Image.Image,
        prompt: str = "",
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        no_repeat_ngram_size: Optional[int] = None,  # not supported by vllm
        max_new_tokens: Optional[int] = None,
    ) -> str:
        return self.batch_predict(
            [image],  # type: ignore
            [prompt],
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_new_tokens=max_new_tokens,
        )[0]

    def batch_predict(
        self,
        images: List[str] | List[bytes] | List[Image.Image],
        prompts: Union[List[str], str] = "",
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        no_repeat_ngram_size: Optional[int] = None,  # not supported by vllm
        max_new_tokens: Optional[int] = None,
    ) -> List[str]:
        if isinstance(prompts, list):
            assert len(prompts) == len(images), "Length of prompts and images must match."

        sp = self.build_sampling_params(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            repetition_penalty=repetition_penalty,
            no_repeat_ngram_size=no_repeat_ngram_size,
            max_new_tokens=max_new_tokens,
        )

        vllm_sp_dict = {
            "temperature": sp.temperature,
            "top_p": sp.top_p,
            "top_k": sp.top_k,
            "presence_penalty": sp.presence_penalty,
            "frequency_penalty": sp.frequency_penalty,
            "repetition_penalty": sp.repetition_penalty,
            # max_tokens should smaller than model max length
            "max_tokens": sp.max_new_tokens if sp.max_new_tokens is not None else self.model_max_length,
        }

        vllm_sampling_params = self.VllmSamplingParams(
            **{k: v for k, v in vllm_sp_dict.items() if v is not None},
            skip_special_tokens=False,
        )

        image_objs: list[Image.Image] = []
        for image in images:
            if isinstance(image, str):
                image = load_resource(image)
            if not isinstance(image, Image.Image):
                image = Image.open(BytesIO(image))
            image = get_rgb_image(image)
            image_objs.append(image)

        if isinstance(prompts, str):
            chat_prompts: list[str] = [
                self.tokenizer.apply_chat_template(
                    self.build_messages(prompts),  # type: ignore
                    tokenize=False,
                    add_generation_prompt=True,
                )
            ] * len(images)
        else:  # isinstance(prompts, list)
            chat_prompts: list[str] = [
                self.tokenizer.apply_chat_template(
                    self.build_messages(prompt),  # type: ignore
                    tokenize=False,
                    add_generation_prompt=True,
                )
                for prompt in prompts
            ]

        outputs = []
        batch_size = self.batch_size if self.batch_size > 0 else len(images)

        for i in range(0, len(images), batch_size):
            batch_image_objs = image_objs[i : i + batch_size]
            batch_chat_prompts = chat_prompts[i : i + batch_size]
            batch_outputs = self._predict_one_batch(
                batch_image_objs,
                batch_chat_prompts,
                vllm_sampling_params,
            )
            outputs.extend(batch_outputs)

        return outputs

    def _predict_one_batch(
        self,
        image_objs: List[Image.Image],
        chat_prompts: List[str],
        vllm_sampling_params: "SamplingParams",
    ):
        vllm_prompts = [
            {"prompt": chat_prompt, "multi_modal_data": {"image": image}}
            for chat_prompt, image in zip(chat_prompts, image_objs)
        ]

        outputs = self.vllm_llm.generate(
            prompts=vllm_prompts,  # type: ignore
            sampling_params=vllm_sampling_params,
        )

        return [self.get_output_content(output) for output in outputs]

    async def aio_predict(
        self,
        image: str | bytes | Image.Image,
        prompt: str = "",
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        no_repeat_ngram_size: Optional[int] = None,  # not supported by vllm
        max_new_tokens: Optional[int] = None,
    ) -> str:
        raise UnsupportedError(
            "Asynchronous aio_predict() is not supported in TransformersVlmClient. Please use predict() instead."
        )

    async def aio_batch_predict(
        self,
        images: List[str] | List[bytes] | List[Image.Image],
        prompts: Union[List[str], str] = "",
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        repetition_penalty: Optional[float] = None,
        no_repeat_ngram_size: Optional[int] = None,  # not supported by vllm
        max_new_tokens: Optional[int] = None,
        semaphore: asyncio.Semaphore | None = None,
    ) -> List[str]:
        raise UnsupportedError(
            "Asynchronous aio_batch_predict() is not supported in TransformersVlmClient. Please use batch_predict() instead."
        )
