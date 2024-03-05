import sys, io

import openai
import json
import time
from contextlib import contextmanager

t = type

sys_prompt = "Help me to debug Python exceptions"


# Function to process streaming output
def process_output(stream):
    for chunk in stream:
        # print(chunk)
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


def install(openai_token: str):
    # TODO: make it work in Ipython
    def smart_handler(type, value, traceback):
        with open(traceback.tb_frame.f_code.co_filename, encoding="utf8") as codefile:
            code = codefile.read()

        with redirect_stderr() as buffer:
            sys.__excepthook__(type, value, traceback)
            trace = buffer.getvalue()

        print(trace)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": f"```{code}```"},
                {"role": "user", "content": trace},
            ],
            stream=True,
        )
        process_output(response)

    client = openai.OpenAI(api_key=openai_token)
    sys.excepthook = smart_handler
