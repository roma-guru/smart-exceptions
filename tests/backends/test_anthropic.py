import pytest
from unittest.mock import patch, MagicMock, sentinel
from smart_exceptions.backends.anthropic import Claude


@pytest.fixture
def mock_claude():
    with patch("smart_exceptions.backends.anthropic.anthropic") as mock_anthropic:
        backend = Claude("test_token", lang="en", send_code=True, proxy=None)
        assert mock_anthropic.Anthropic.called
        yield backend


def test_send_request(mock_claude):
    mock_claude._send_request(sentinel.gpt_request, stream=False)
    assert mock_claude.client.messages.create.called
    mock_claude.client.reset_mock()

    with pytest.raises(StopIteration):
        next(mock_claude._send_request(sentinel.gpt_request, stream=True))
    assert mock_claude.client.messages.stream.called


def test_prepare_request(mock_claude):
    res = mock_claude._prepare_request((ValueError, ValueError("test"), None))
    assert type(res) == list
    for item in res:
        assert type(item) == dict
        assert item.keys() == {"role", "content"}


def test_extract_answer(mock_claude):
    mock_response = MagicMock()
    mock_response.content[0].text = "test"
    assert mock_claude._extract_answer(mock_response) == "test"


def test_extract_delta(mock_claude):
    assert mock_claude._extract_delta("test") == "test"
