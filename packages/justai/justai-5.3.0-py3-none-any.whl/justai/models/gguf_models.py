from typing import Any

from justai.model.message import Message

try:
    from llama_cpp import Llama
except ImportError:
    raise ImportError("If you want to use Llama models with justai run `pip install justai[llama]`")


from justai.models.basemodel import BaseModel


class GuffModel(BaseModel):
    def __init__(self, model_name: str, params: dict):
        """Model implemention should create attributes for all supported parameters"""
        system_message = f"You are {model_name.split('/')[-1]}, a large open source language model."
        super().__init__(model_name, params, system_message)

        # Client
        self.client = Llama(
            model_path=model_name,
            temperature=self.temperature,
            n_ctx=self.n_ctx,
            n_batch=self.n_batch,
            n_threads=self.n_threads,
            n_gpu_layers=self.n_gpu_layers,
            verbose=False,
            seed=42,
        )

        # Model specific parameters
        self.model_params["n_ctx"] = params.get("n_ctx", 8192)  # Max tokens for prompt and response combined
        # 0 for CPU only, 1 for Metal, otherwise dependent on GPU-type
        self.model_params["n_gpu_layers"] = params.get("n_gpu_layers", 1)
        self.model_params["n_threads"] = params.get("n_threads", 4)
        self.model_params["temperature"] = params.get("temperature", 0.8)
        self.model_params["n_batch"] = params.get("n_batch", 512)

    def chat(
        self, messages: list[Message], return_json: bool, response_format, use_cache: bool = False, max_retries=None
    ) -> tuple[[str | object], int, int]:
        if response_format:
            raise NotImplementedError("GUFF models do not support response_format")

        system = messages[0]["content"]
        message = f"<s>[INST] <<SYS>>{system}<</SYS>>{messages[-1]['content']}[/INST]"
        output = self.client(message, echo=True, stream=False)
        if self.debug:
            print(output["choices"][0]["text"] + "\n")
        output_text = output["choices"][0]["text"].split("[/INST]")[1].strip()
        if output["choices"][0]["text"][0] == '"' and output_text[-1] == '"':
            output_text = output_text[:-1]
        if not output_text:
            output_text = "Model produced no result"
        elif output_text[-1] != ".":
            try:
                a, b = output_text.replace("\n", " ").rsplit(". ", 1)
                output_text = a + ". [" + b + "]"
            except ValueError:
                pass
        prompt_tokens = output["usage"]["prompt_tokens"]
        completion_tokens = output["usage"]["completion_tokens"]
        return output_text, prompt_tokens, completion_tokens

    def chat_async(self, messages: list[Message]) -> tuple[Any, int, int]:
        print("chat_async not implemented for GUFF models")
        return self.chat(messages, False, response_format=None)

    def token_count(self, text: str) -> int:
        return 0
