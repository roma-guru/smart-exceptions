import sys
import io
import os

import openai
from contextlib import contextmanager

client = None
sys_prompt = "Help me to debug Python exceptions"
last_request = None


# Function to process streaming output
def process_output(stream):
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")


@contextmanager
def redirect_stderr():
    try:
        buffer = io.StringIO()
        sys.stderr = buffer
        yield buffer
    finally:
        sys.stderr = sys.__stderr__


def install(openai_token: str=None, explicit=False):
    # TODO: make it work in Ipython
    global client
    if openai_token is None:
        try:
            openai_token = os.environ['OPENAI_TOKEN']
        except KeyError:
            raise ValueError("Please provide OpenAI token via param or $OPENAI_TOKEN var")

    def smart_handler(type, value, traceback):
        global last_request

        filename = traceback.tb_frame.f_code.co_filename
        print(filename)
        with open(filename, encoding="utf8") as codefile:
            code = codefile.read()

        with redirect_stderr() as buffer:
            sys.__excepthook__(type, value, traceback)
            trace = buffer.getvalue()

        print(trace)

        last_request = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": f"```{code}```"},
            {"role": "user", "content": trace},
        ]

        if not explicit:
            ask_gpt()
    
    client = openai.OpenAI(api_key=openai_token)
    sys.excepthook = smart_handler


def ask_gpt():
    global client, last_request

    if client is None:
        raise ValueError("Please call install() first!")

    if last_request is not None:
        print("Asking ChatGPT...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=last_request,
            stream=True,
        )
        process_output(response)
