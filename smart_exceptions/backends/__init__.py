from .openai import ChatGPT
from .anthropic import Claude

def get_by_name(name: str) -> type:
    if name.lower()=="openai":
        return ChatGPT
    elif name.lower()=="claude":
        return Claude

    raise ValueError("unknown backend")

