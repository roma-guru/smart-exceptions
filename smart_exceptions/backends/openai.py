from typing import Optional, Tuple, Any

import openai
import httpx

from .base import GPTBackend


class ChatGPT(GPTBackend):
    model = "gpt-3.5-turbo"
    color = "green"

    def __init__(
        self, api_token: str, *, lang: str, send_code: bool, proxy: Optional[str]
    ):
        super().__init__(lang, send_code)
        self.client = openai.OpenAI(
            api_key=api_token, http_client=httpx.Client(proxy=proxy)
        )
