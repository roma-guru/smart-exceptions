import sys
from abc import ABC
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
    MAX_CODE_LEN = 100000

    SYSTEM_ROLE = "system"
    USER_ROLE = "user"
    ASSISTENT_ROLE = "assistent"

    sys_prompt = """
        Help me to debug Python exceptions.
        Use Markdown with sections.
        Answer in {lang}.
        """
    # Override fields
    model = None
    color = None
    client = None

    def __init__(self, lang: str, send_code: bool):
        self.lang = lang
        self.send_code = send_code

    def _prepare_trace_and_code(
        self, exc_info: Optional[ExcInfo], send_code: bool
    ) -> Tuple[str]:
        type, value, traceback = exc_info

        code = None
        filename = traceback.tb_frame.f_code.co_filename
        # TODO: detect console
        try:
            if send_code:
                with open(filename, encoding="utf8") as codefile:
                    code = codefile.read()
                    code = code[: self.MAX_CODE_LEN]
        except IOError:
            print("[red]Can't read code file[/red], ignoring...")

        with redirect_stderr() as buffer:
            print_exception(type, value, traceback)
            trace = buffer.getvalue()

        return trace, code

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
        trace, code = self._prepare_trace_and_code(exc_info, self.send_code)
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
        print(f"Asking [bold {self.color}]{type(self).__name__}...[/bold {self.color}]")
        request = self._prepare_request(exc_info)
        response = self._send_request(request, stream)

        answer = self._print_response(response, stream)

        if not dialog:
            return

        while prompt := input("User: "):
            request.append({"role": self.ASSISTENT_ROLE, "content": answer})
            request.append({"role": self.USER_ROLE, "content": prompt})
            response = self._send_request(request, stream)
            answer = self._print_response(response, stream)

    def _print_response(self, response: GPTResponse, stream: bool) -> str:
        print("GPT: ", end="")
        if stream:
            ...
        else:
            answer = response.choices[0].message.content

        print(Markdown(answer))
        return answer
