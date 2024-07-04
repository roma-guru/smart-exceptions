from typing import Any, Tuple

import groq
import httpx

from .base import ExcInfo, GPTBackend, GPTRequest, GPTResponse


class Groq(GPTBackend):
    model = "mixtral-8x7b-32768"
    color = "orange1"

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
                model=self.model, messages=gpt_request, stream=True
            )

        return self.client.chat.completions.create(
            model=self.model,
            messages=gpt_request,
        )

    def _prepare_request(self, exc_info: ExcInfo) -> GPTRequest:
        trace = self._prepare_trace(exc_info)
        code = self._prepare_code(exc_info)

        gpt_request = [
            {
                "role": self.SYSTEM_ROLE,
                "content": self.sys_prompt.format(lang=self.lang),
            },
            {"role": self.USER_ROLE, "content": f"```{code}```"},
            {"role": self.USER_ROLE, "content": trace},
        ]
        return gpt_request

    def _extract_answer(self, response: GPTResponse) -> str:
        return response.choices[0].message.content

    def _extract_delta(self, chunk: Any) -> str:
        return chunk.choices[0].delta.content
