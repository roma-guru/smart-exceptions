import io
import os
import sys

from rich import print
from rich.traceback import Traceback

from .backends import get_by_name

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


def install_handler():
    """
    Install global exception handler.
    That won't work in debug console and Ipython.
    """
    global gpt_backend

    def smart_handler(type, value, traceback):
        print(
            Traceback.from_exception(
                type, value, traceback, show_locals=True, max_frames=10
            )
        )

        exc_info = (type, value, traceback)
        gpt_backend.ask_gpt(exc_info, dialog=False)

    sys.excepthook = smart_handler


def ask(*, dialog=False):
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
