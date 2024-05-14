from typing import Optional, Tuple, Any

import groq
import httpx

from .base import GPTBackend, GPTRequest


class Groq(GPTBackend):
    model = "mixtral-8x7b-32768"
    color = "orange"

    def __init__(
        self, api_token: str, *, lang: str, send_code: bool, proxy: str | None
    ):
        super().__init__(lang, send_code)
        self.client = groq.Groq(
            api_key=api_token, http_client=httpx.Client(proxy=proxy)
        )

    def _send_request(self, gpt_request: GPTRequest, stream: bool) -> Any:
        if stream:
            return self.client.chat.completions.create(
                model=self.model, messages=gpt_request, streaming=True
            )

        return self.client.chat.completions.create(
            model=self.model,
            messages=gpt_request,
        )
