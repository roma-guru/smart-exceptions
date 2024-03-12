import sys
from abc import ABC
from traceback import print_exception
from typing import Tuple, Optional, Any

from ..utils import redirect_stderr

class GPTBackend(ABC):
    MAX_CODE_LEN = 100000

    def _prepare_request(self, exc_info: Optional[Tuple[Any]], send_code: bool) -> Tuple[str]:
        type, value, traceback = exc_info

        code = None
        filename = traceback.tb_frame.f_code.co_filename
        #TODO: detect console
        try:
            if send_code:
                with open(filename, encoding="utf8") as codefile:
                    code = codefile.read()
                    code = code[:self.MAX_CODE_LEN]
        except IOError:
            print("[red]Can't read code file[/red], ignoring...")

        with redirect_stderr() as buffer:
            print_exception(type, value, traceback)
            trace = buffer.getvalue()

        return (trace, code)


