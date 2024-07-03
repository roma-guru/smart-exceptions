import pytest
from smart_exceptions.backends import get_by_name, ChatGPT


def test_get_by_name():
    assert get_by_name("chatgpt") == ChatGPT
    with pytest.raises(ValueError):
        get_by_name("unknown")
