from typing import Optional, Tuple, Any

import anthropic
import httpx
from rich import print
from rich.markdown import Markdown

from .base import GPTBackend

sys_prompt = """
    Help me to debug Python exceptions.
    Use Markdown with sections.
    Answer in {lang}.
    """

class Claude(GPTBackend):
    def __init__(self, api_token: str, *, lang: str, send_code: bool, proxy: Optional[str]):
        self.lang = lang
        self.send_code = send_code
        self.client = anthropic.Anthropic(api_key=api_token, http_client=httpx.Client(proxy=proxy))

    def ask_gpt(self, exc_info: Tuple[Any], /, *, dialog: bool):
        trace, code = self._prepare_request(exc_info, self.send_code)
        gpt_request = [
            {"role": "user", "content": f"```{code}```\n{trace}"},
        ]

        print("Asking [bold green]Claude...[/bold green]")
        response = self.client.messages.create(
            system=sys_prompt.format(lang=self.lang),
            model="claude-instant-1.2",
            messages=gpt_request,
            max_tokens=1024,
        )
        print(Markdown(response.content[0].text))

