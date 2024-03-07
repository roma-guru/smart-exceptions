import sys
import io
import os
import httpx

from rich import print
from rich.markdown import Markdown
from rich.traceback import Traceback

import openai
from contextlib import contextmanager

client = None
sys_prompt = """
    Help me to debug Python exceptions. 
    Use Markdown with sections.
    Answer in {lang}.
    """
last_request = None


@contextmanager
def redirect_stderr():
    try:
        buffer = io.StringIO()
        sys.stderr = buffer
        yield buffer
    finally:
        sys.stderr = sys.__stderr__


def install(openai_token: str=None, explicit=False, lang="english", proxy=None):
    # TODO: make it work in Ipython
    global client
    if openai_token is None:
        try:
            openai_token = os.environ['OPENAI_TOKEN']
        except KeyError:
            raise ValueError("Please provide OpenAI token via param or $OPENAI_TOKEN var")

    if proxy is None:
        proxy = os.environ.get('OPENAI_PROXY')


    def smart_handler(type, value, traceback):
        global last_request

        filename = traceback.tb_frame.f_code.co_filename
        print(filename)
        with open(filename, encoding="utf8") as codefile:
            code = codefile.read()

        with redirect_stderr() as buffer:
            sys.__excepthook__(type, value, traceback)
            trace = buffer.getvalue()

        print(Traceback.from_exception(
            type, value, traceback,
            show_locals=True, max_frames=10
        ))

        last_request = [
            {"role": "system", "content": sys_prompt.format(lang=lang)},
            {"role": "user", "content": f"```{code}```"},
            {"role": "user", "content": trace},
        ]

        if not explicit:
            ask_gpt()
    
    client = openai.OpenAI(api_key=openai_token, http_client=httpx.Client(proxy=proxy))
    sys.excepthook = smart_handler


def ask_gpt():
    global client, last_request

    if client is None:
        raise ValueError("Please call install() first!")

    if last_request is not None:
        print("Asking [bold green]ChatGPT...[/bold green]")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=last_request,
        )
        print(Markdown(response.choices[0].message.content))
