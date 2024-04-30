import anthropic
import httpx

from .base import GPTBackend


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
