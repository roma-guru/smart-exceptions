from abc import ABC
from io import StringIO
from traceback import print_exception
from typing import Tuple, Optional, Any, List, Dict, Union

from ..utils import redirect_stderr

from rich import print
from rich.markdown import Markdown

GPTRequest = List[Dict[str, str]]
GPTResponse = Union[...]
ExcInfo = Tuple[Any]


class GPTBackend(ABC):
    # TODO: count tokens instead
    MAX_CODE_LEN = 10000
    MAX_TOKENS = 1000

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

    def _prepare_code(self, exc_info: Optional[ExcInfo]) -> str:
        type, value, traceback = exc_info

        code = None
        if not self.send_code:
            return code
        filename = traceback.tb_frame.f_code.co_filename
        try:
            with open(filename, encoding="utf8") as codefile:
                code = codefile.read()
                code = code[: self.MAX_CODE_LEN]
        except IOError:
            print("[red]Can't read code file[/red], ignoring...")

    def _prepare_trace(self, exc_info: ExcInfo) -> str:
        type, value, traceback = exc_info

        with redirect_stderr() as buffer:
            print_exception(type, value, traceback)
            trace = buffer.getvalue()

        return trace

    def _send_request(self, gpt_request: GPTRequest, stream: bool) -> Any:
        if stream:
            return self.client.chat.completions.create(
                model=self.model, messages=gpt_request, streaming=True
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

    def ask_gpt(
        self, exc_info: ExcInfo, /, *, dialog: bool = False, stream: bool = False
    ):
        print(f"Asking [bold {self.color}]{self.name}...[/bold {self.color}]")
        request = self._prepare_request(exc_info)
        response = self._send_request(request, stream)

        answer = self._print_response(response, stream)

        if not dialog:
            return

        print("=" * 100)
        while prompt := input("User: "):
            request.append({"role": self.ASSISTENT_ROLE, "content": answer})
            request.append({"role": self.USER_ROLE, "content": prompt})
            response = self._send_request(request, stream)
            print("-" * 100)
            answer = self._print_response(response, stream)
            print("=" * 100)

    def _extract_answer(self, response: GPTResponse):
        return response.choices[0].message.content

    def _print_and_aggregate(self, response: GPTResponse):
        buf = StringIO()
        for chunk in response:
            buf.write(chunk)
            print(chunk)
        return buf.getvalue()

    def _print_response(self, response: GPTResponse, stream: bool) -> str:
        print(f"[bold {self.color}]{self.name}[/bold {self.color}]")
        # TODO: check error
        if stream:
            answer = self._print_and_aggregate(response)
            print("\b" * len(answer))
        else:
            answer = self._extract_answer(response)

        print(Markdown(answer))
        return answer
