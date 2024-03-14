from typing import Any, Optional, Tuple

import google.generativeai as genai
import httpx
from rich import print
from rich.markdown import Markdown

from .base import GPTBackend

sys_prompt = """
    Help me to debug Python exceptions.
    Use Markdown with sections.
    Answer in {lang}.
    """


class Gemini(GPTBackend):
    def __init__(
        self, api_token: str, *, lang: str, send_code: bool, proxy: Optional[str]
    ):
        self.lang = lang
        self.send_code = send_code
        genai.configure(api_key=api_token)

    def ask_gpt(self, exc_info: Tuple[Any], /, *, dialog: bool):
        trace, code = self._prepare_request(exc_info, self.send_code)

        print("Asking [bold green]Bard/Gemini...[/bold green]")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([sys_prompt, f"```{code}```", trace])
        print(Markdown(response.text))
