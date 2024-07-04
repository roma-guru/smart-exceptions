from unittest.mock import patch, MagicMock, sentinel
import pytest
from smart_exceptions.backends.groq import Groq


@pytest.fixture
def mock_groq():
    with patch("smart_exceptions.backends.groq.groq") as mock_openai:
        backend = Groq("test_token", lang="en", send_code=True, proxy=None)
        assert mock_openai.Groq.called
        yield backend


def test_send_request(mock_groq):
    mock_groq._send_request(sentinel.gpt_request, stream=True)
    assert mock_groq.client.chat.completions.create.called_with(stream=True)
    mock_groq.client.reset_mock()

    mock_groq._send_request(sentinel.gpt_request, stream=False)
    assert mock_groq.client.chat.completions.create.called


def test_prepare_request(mock_groq):
    res = mock_groq._prepare_request((ValueError, ValueError("test"), None))
    assert type(res) == list
    for item in res:
        assert type(item) == dict
        assert item.keys() == {"role", "content"}


def test_extract_answer(mock_groq):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "test"
    assert mock_groq._extract_answer(mock_response) == "test"


def test_extract_delta(mock_groq):
    mock_response = MagicMock()
    mock_response.choices[0].delta.content = "test"
    assert mock_groq._extract_delta(mock_response) == "test"
