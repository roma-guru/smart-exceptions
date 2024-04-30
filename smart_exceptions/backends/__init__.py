from .openai import ChatGPT
from .anthropic import Claude
from .groq import Groq


def get_by_name(name: str) -> type:
    name = name.lower()
    classes = (ChatGPT, Claude, Groq)
    for cl in classes:
        if cl.__name__.lower() == name:
            return cl

    raise ValueError("unknown backend")
