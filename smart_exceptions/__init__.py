import sys
import io
import os
import httpx

from traceback import print_exception
from rich import print
from rich.markdown import Markdown
from rich.traceback import Traceback

import openai
from contextlib import contextmanager

MAX_CODE_LEN = 10000

client = None
sys_prompt = """
    Help me to debug Python exceptions. 
    Use Markdown with sections.
    Answer in {lang}.
    """


@contextmanager
def redirect_stderr():
    try:
        buffer = io.StringIO()
        sys.stderr = buffer
        yield buffer
    finally:
        sys.stderr = sys.__stderr__


def install(openai_token: str=None, *, explicit=False, lang="english", proxy=None):
    global client
    if openai_token is None:
        try:
            openai_token = os.environ['OPENAI_TOKEN']
        except KeyError:
            raise ValueError("Please provide OpenAI token via param or $OPENAI_TOKEN var")

    if proxy is None:
        proxy = os.environ.get('OPENAI_PROXY')


    def smart_handler(type, value, traceback):
        print(Traceback.from_exception(
            type, value, traceback,
            show_locals=True, max_frames=10
        ))

        exc_info = (type, value, traceback)
        ask_gpt(exc_info, lang)
    
    client = openai.OpenAI(api_key=openai_token, http_client=httpx.Client(proxy=proxy))
    if not explicit:
        sys.excepthook = smart_handler


def ask_gpt(exc_info=None, lang="english"):
    global client
    if client is None:
        raise ValueError("Please call install() first!")

    if exc_info is None:
        exc_info=(sys.last_type, sys.last_value, sys.last_traceback)
    type, value, traceback = exc_info

    code = None
    filename = traceback.tb_frame.f_code.co_filename
    try:
        with open(filename, encoding="utf8") as codefile:
            code = codefile.read()
            code = code[:MAX_CODE_LEN]
    except IOError:
        print("[red]Can't read code file[/red], ignoring...")

    with redirect_stderr() as buffer:
        print_exception(type, value, traceback)
        trace = buffer.getvalue()

    gpt_request = [
        {"role": "system", "content": sys_prompt.format(lang=lang)},
        {"role": "user", "content": f"```{code}```"},
        {"role": "user", "content": trace},
    ]

    print("Asking [bold green]ChatGPT...[/bold green]")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=gpt_request,
    )
    print(Markdown(response.choices[0].message.content))
