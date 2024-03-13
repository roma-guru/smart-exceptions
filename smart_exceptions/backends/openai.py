from typing import Optional, Tuple, Any

import openai
import httpx
from rich import print
from rich.markdown import Markdown

from .base import GPTBackend

sys_prompt = """
    Help me to debug Python exceptions. 
    Use Markdown with sections.
    Answer in {lang}.
    """

class ChatGPT(GPTBackend):
    def __init__(self, api_token: str, *, lang: str, send_code: bool, proxy: Optional[str]):
        self.lang = lang
        self.send_code = send_code
        self.client = openai.OpenAI(api_key=api_token, http_client=httpx.Client(proxy=proxy))

    def ask_gpt(self, exc_info: Tuple[Any], /, *, dialog: bool):
        trace, code = self._prepare_request(exc_info, self.send_code)
        gpt_request = [
            {"role": "system", "content": sys_prompt.format(lang=self.lang)},
            {"role": "user", "content": f"```{code}```"},
            {"role": "user", "content": trace},
        ]

        print("Asking [bold green]ChatGPT...[/bold green]")
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=gpt_request,
        )
        print(Markdown(response.choices[0].message.content))

