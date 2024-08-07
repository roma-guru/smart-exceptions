from abc import ABC, abstractmethod
from io import StringIO
from traceback import print_exception
from typing import Any, Dict, List, Tuple

import tiktoken
from rich import print
from rich.live import Live
from rich.markdown import Markdown

from ..utils import redirect_stderr

GPTRequest = List[Dict[str, str]]
GPTResponse = Any
ExcInfo = Tuple[Any]


class GPTBackend(ABC):
    # max context size in tokens, 4k is a safe choice
    MAX_TOKENS = 4000

    SYSTEM_ROLE = "system"
    USER_ROLE = "user"
    ASSISTENT_ROLE = "assistant"

    sys_prompt = """
        Help me to debug Python exceptions.
        Use Markdown with sections.
        Answer in {lang}.
        """
    # Override fields in subs
    model = None
    color = None
    client = None

    def __init__(self, lang: str, send_code: bool):
        self.lang = lang
        self.name = type(self).__name__
        self.send_code = send_code

    def _prepare_code(self, exc_info: ExcInfo) -> str:
        type, value, traceback = exc_info

        code = ""
        if not self.send_code or traceback is None:
            return code
        filename = traceback.tb_frame.f_code.co_filename
        try:
            with open(filename, encoding="utf8") as codefile:
                code = codefile.read()
        except IOError:
            print("[red]Can't read code file[/red], ignoring...")

        return self._limit_tokens(code)

    def _prepare_trace(self, exc_info: ExcInfo) -> str:
        type, value, traceback = exc_info

        trace = ""
        if traceback is None:
            return trace

        with redirect_stderr() as buffer:
            print_exception(type, value, traceback)
            trace = buffer.getvalue()

        return self._limit_tokens(trace)

    def _limit_tokens(self, text: str) -> str:
        if not text:
            return text

        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(text)
        return encoding.decode(tokens[: self.MAX_TOKENS])

    # override in subs
    @abstractmethod
    def _send_request(self, gpt_request: GPTRequest, stream: bool) -> Any:
        return NotImplemented  # pragma: no cover

    @abstractmethod
    def _prepare_request(self, exc_info: ExcInfo) -> GPTRequest:
        return NotImplemented  # pragma: no cover

    @abstractmethod
    def _extract_answer(self, response: GPTResponse) -> str:
        return NotImplemented  # pragma: no cover

    @abstractmethod
    def _extract_delta(self, chunk: Any) -> str:
        return NotImplemented  # pragma: no cover

    def ask_gpt(
        self, exc_info: ExcInfo, /, *, dialog: bool = False, stream: bool = False
    ):
        print(f"Asking [bold {self.color}]{self.name}[/bold {self.color}] ...")
        request = self._prepare_request(exc_info)
        response = self._send_request(request, stream)

        answer = self._print_response(response, stream)

        if not dialog:
            return

        print("=" * 100)
        while True:
            print(
                "[bold magenta]User[/bold magenta] ([italic]leave empty to finish[/italic]): ",
                end="",
            )
            prompt = input()
            if not prompt:
                break
            request.append({"role": self.ASSISTENT_ROLE, "content": answer})
            request.append({"role": self.USER_ROLE, "content": prompt})
            response = self._send_request(request, stream)
            print("-" * 100)
            answer = self._print_response(response, stream)
            print("=" * 100)

    def _print_and_aggregate(self, response: GPTResponse) -> str:
        buf = StringIO()
        with Live("...", transient=True, screen=False) as live:
            for chunk in response:
                text = self._extract_delta(chunk)
                if text is not None:
                    buf.write(text)
                    live.update(buf.getvalue())

        return buf.getvalue()

    def _print_response(self, response: GPTResponse, stream: bool) -> str:
        print(f"[bold {self.color}]{self.name}:[/bold {self.color}]")
        if stream:
            answer = self._print_and_aggregate(response)
        else:
            answer = self._extract_answer(response)

        print(Markdown(answer))
        return answer
