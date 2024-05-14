import os
import sys

from rich import print
from rich.traceback import Traceback
from traceback import print_exception

from .backends import get_by_name
from .run_env import detect_env

gpt_backend = None


def init(
    api_token: str = None,
    *,
    lang="english",
    proxy=None,
    send_code=True,
    backend="chatgpt",
):
    """
    Init GPT backend for future use:
    either implicitly with install exception handler OR asking explicitly.
    Must be called explicitly first!

    api_token: GPT API token
    lang: language of answer, default English
    proxy: proxy to use for requests, default None
    send_code: send code along with a stacktrace, default True
    backend: GPT backend to use, default OpenAI
    """
    global gpt_backend
    if api_token is None:
        try:
            api_token = os.environ[f"{backend.upper()}_TOKEN"]
        except KeyError:
            raise ValueError(
                f"Please provide GPT api token via param or ${backend.upper()}_TOKEN var"
            )

    if proxy is None:
        proxy = os.environ.get(f"{backend.upper()}_PROXY")

    gpt_backend = get_by_name(backend)(
        api_token, lang=lang, proxy=proxy, send_code=send_code
    )


def install_handler(show_locals=True, max_frames=5, dialog=False):
    """
    Install global exception handler.
    That won't work in debug console and Ipython.

    show_locals: show local variable in pretty mode (too many for Ipython)
    max_frames: number of displayed stackframes
    dialog: continue chat after initial answer
    """
    global gpt_backend

    run_env = detect_env()
    print(f"Detected [italic]{run_env}[/italic]")

    def smart_handler(type, value, traceback):
        if run_env == "python":
            print(
                Traceback.from_exception(
                    type,
                    value,
                    traceback,
                    show_locals=show_locals,
                    max_frames=max_frames,
                )
            )
        else:
            print_exception(type, value, traceback)

        exc_info = (type, value, traceback)
        gpt_backend.ask_gpt(exc_info, dialog=dialog)

    def smart_ipy_handler(_, type, value, traceback, **kwargs):  # pragma: no cover
        smart_handler(type, value, traceback)

    if run_env == "ipython":
        show_locals = False
        get_ipython().set_custom_exc((Exception,), smart_ipy_handler)  # noqa
    else:
        sys.excepthook = smart_handler


def ask(*, dialog=True):
    """
    Ask GPT about last exception explicitly.
    Suitable for debug console and Ipython.

    dialog: continue the chat after an answer, default False
    """
    global gpt_backend
    if gpt_backend is None:
        raise ValueError("Please call init() first!")

    try:
        exc_info = (sys.last_type, sys.last_value, sys.last_traceback)
    except AttributeError:
        exc_info = sys.exc_info()

    if exc_info == (None, None, None):
        print("[bold yellow]WARN[/bold yellow] no exceptions yet")
    else:
        gpt_backend.ask_gpt(exc_info, dialog=dialog)
