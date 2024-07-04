import pytest
from unittest.mock import patch, MagicMock, sentinel
from smart_exceptions.backends.openai import ChatGPT


@pytest.fixture
def mock_chatgpt():
    with patch("smart_exceptions.backends.openai.openai") as mock_openai:
        backend = ChatGPT("test_token", lang="en", send_code=True, proxy=None)
        assert mock_openai.OpenAI.called
        yield backend


def test_send_request(mock_chatgpt):
    mock_chatgpt._send_request(sentinel.gpt_request, stream=True)
    assert mock_chatgpt.client.chat.completions.create.called_with(stream=True)
    mock_chatgpt.client.reset_mock()

    mock_chatgpt._send_request(sentinel.gpt_request, stream=False)
    assert mock_chatgpt.client.chat.completions.create.called_with(stream=False)


def test_prepare_request(mock_chatgpt):
    res = mock_chatgpt._prepare_request((ValueError, ValueError("test"), None))
    assert type(res) == list
    for item in res:
        assert type(item) == dict
        assert item.keys() == {"role", "content"}


def test_extract_answer(mock_chatgpt):
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "test"
    assert mock_chatgpt._extract_answer(mock_response) == "test"


def test_extract_delta(mock_chatgpt):
    mock_response = MagicMock()
    mock_response.choices[0].delta.content = "test"
    assert mock_chatgpt._extract_delta(mock_response) == "test"
