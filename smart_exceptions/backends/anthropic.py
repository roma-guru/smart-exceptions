from typing import Any

import anthropic
import httpx

from .base import ExcInfo, GPTBackend, GPTRequest, GPTResponse


class Claude(GPTBackend):
    model = "claude-instant-1.2"
    color = "orange3"

    def __init__(
        self, api_token: str, *, lang: str, send_code: bool, proxy: str | None
    ):
        super().__init__(lang, send_code)
        self.client = anthropic.Anthropic(
            api_key=api_token, http_client=httpx.Client(proxy=proxy)
        )

    def _prepare_request(self, exc_info: ExcInfo) -> GPTRequest:
        trace = self._prepare_trace(exc_info)
        code = self._prepare_code(exc_info)

        gpt_request = [
            {"role": self.USER_ROLE, "content": f"```{code}```\n\n{trace}"},
        ]
        return gpt_request

    def _chunk_gen(self, sys_message: str, gpt_request: GPTRequest):
        with self.client.messages.stream(
            model=self.model,
            messages=gpt_request,
            max_tokens=self.MAX_TOKENS,
            system=sys_message,
        ) as stream_obj:
            yield from stream_obj.text_stream

    def _send_request(self, gpt_request: GPTRequest, stream: bool) -> Any:
        sys_message = self.sys_prompt.format(lang=self.lang)
        if stream:
            return self._chunk_gen(sys_message, gpt_request)

        return self.client.messages.create(
            model=self.model,
            messages=gpt_request,
            max_tokens=self.MAX_TOKENS,
            system=sys_message,
        )

    def _extract_answer(self, response: GPTResponse) -> str:
        return response.content[0].text

    def _extract_delta(self, chunk: Any) -> str:
        return chunk
