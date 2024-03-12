from .openai import OpenAI

def get_by_name(name: str) -> type:
    if name.lower()=="openai":
        return OpenAI

    raise ValueError("unknown backend")

