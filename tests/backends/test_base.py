from smart_exceptions.backends.base import GPTBackend, GPTRequest, GPTResponse, ExcInfo
from typing import Any, Dict, List, Optional, Tuple, Union
import pytest
from unittest.mock import MagicMock, patch
import io
from rich.markdown import Markdown


class TestGPTBackend(GPTBackend):
    def _send_request(self, gpt_request: GPTRequest, stream: bool) -> Any:
        pass

    def _prepare_request(self, exc_info: ExcInfo) -> GPTRequest:
        pass

    def _extract_answer(self, response: GPTResponse) -> str:
        pass

    def _extract_delta(self, chunk: Any) -> str:
        pass


@pytest.fixture
def mock_backend():
    return TestGPTBackend(lang="en", send_code=True)


@pytest.fixture
def mock_response():
    mock = MagicMock()
    mock.__iter__.return_value = ["test"]
    return mock


@pytest.fixture
def mock_encoding():
    mock = MagicMock()
    mock.encode.side_effect = lambda x: x.split()
    mock.decode.side_effect = lambda x: " ".join(x)

    with patch("smart_exceptions.backends.base.tiktoken") as mock_tiktoken:
        mock_tiktoken.get_encoding.return_value = mock
        yield mock


@pytest.fixture
def mock_traceback(mock_open):
    mock = MagicMock()
    mock.tb_frame.f_code.co_filename = "test.py"
    return mock


@pytest.fixture
def mock_open():
    with patch("builtins.open", return_value=io.StringIO("test_code")) as mock_open:
        yield mock_open


@patch("smart_exceptions.backends.base.print")
@patch("smart_exceptions.backends.base.GPTBackend._limit_tokens")
def test_prepare_code(mock_limit, mock_print, mock_backend, mock_traceback, mock_open):
    mock_limit.side_effect = lambda x: x
    assert mock_backend._prepare_code((ValueError, ValueError("test"), None)) == ""
    assert mock_open.not_called
    assert mock_print.not_called
    assert mock_limit.not_called
    mock_open.reset_mock()
    mock_print.reset_mock()
    mock_limit.reset_mock()

    assert (
        mock_backend._prepare_code((ValueError, ValueError("test"), mock_traceback))
        == "test_code"
    )
    assert mock_open.called_with("test.py", encoding="utf8")
    assert mock_print.not_called
    assert mock_limit.called
    mock_open.reset_mock()
    mock_print.reset_mock()
    mock_limit.reset_mock()

    mock_open.side_effect = IOError
    assert (
        mock_backend._prepare_code((ValueError, ValueError("test"), mock_traceback))
        == ""
    )
    assert mock_open.called_with("test.py", encoding="utf8")
    assert mock_print.called
    assert mock_limit.not_called


@patch("smart_exceptions.backends.base.print_exception")
@patch("smart_exceptions.backends.base.redirect_stderr")
@patch("smart_exceptions.backends.base.GPTBackend._limit_tokens")
def test_prepare_trace(mock_limit, mock_redir, mock_print, mock_backend, mock_traceback, mock_open):
    mock_limit.side_effect = lambda x: x
    mock_redir.return_value.__enter__.return_value.getvalue.return_value = "test_trace"
    assert mock_backend._prepare_trace((ValueError, ValueError("test"), None)) == ""
    assert mock_print.not_called
    assert mock_redir.not_called
    assert mock_open.not_called
    mock_print.reset_mock()
    mock_redir.reset_mock()
    mock_open.reset_mock()

    assert (
        mock_backend._prepare_trace((ValueError, ValueError("test"), mock_traceback)) == "test_trace"
    )
    assert mock_print.called_with(ValueError, ValueError("test"), mock_traceback)
    assert mock_redir.called
    assert mock_limit.called


def test_limit_tokens(mock_backend, mock_encoding):
    assert mock_backend._limit_tokens("") == ""
    assert mock_backend._limit_tokens("test") == "test"
    assert mock_encoding.encode.called
    assert mock_encoding.decode.called

    with patch.object(mock_backend, "MAX_TOKENS", 2):
        assert mock_backend._limit_tokens("test test test") == "test test"
        assert mock_encoding.encode.called
        assert mock_encoding.decode.called


@patch("smart_exceptions.backends.base.print")
def test_print_response(mock_print, mock_backend, mock_response):
    with patch.object(mock_backend, "_extract_answer", return_value="test"):
        assert mock_backend._print_response(mock_response, False) == "test"
        assert mock_backend._extract_answer.called
        assert type(mock_print.call_args[0][0]) == Markdown

    with patch.object(mock_backend, "_print_and_aggregate", return_value="test"):
        assert mock_backend._print_response(mock_response, True) == "test"
        assert mock_backend._print_and_aggregate.called
        assert type(mock_print.call_args[0][0]) == Markdown


@patch("smart_exceptions.backends.base.Live")
def test_print_and_aggregate(mock_live, mock_backend, mock_response):
    with patch.object(mock_backend, "_extract_delta", return_value="test"):
        assert mock_backend._print_and_aggregate(mock_response) == "test"
        assert mock_backend._extract_delta.called
        assert mock_live.return_value.__enter__.return_value.update.called_with("test")


@patch("smart_exceptions.backends.base.print")
@patch("builtins.input")
def test_ask_gpt(
    mock_input,
    mock_print,
    mock_backend,
):
    exc_info = (ValueError, ValueError("test"), None)
    mock_input.side_effect = ["test", ""]

    with (patch.object(mock_backend, "_prepare_request") as mock_prepare_req,
            patch.object(mock_backend, "_send_request") as mock_send_req,
            patch.object(mock_backend, "_print_response") as mock_print_resp):
        mock_send_req.return_value = mock_response

        mock_backend.ask_gpt(exc_info, stream=True, dialog=False)
        assert mock_prepare_req.called_once_with(exc_info)
        assert mock_send_req.called_once_with(mock_prepare_req.return_value, True)
        assert mock_print_resp.called_once_with(mock_send_req.return_value, True)
        assert mock_print.called

        mock_print_resp.reset_mock()
        mock_send_req.reset_mock()
        mock_prepare_req.reset_mock()
        mock_print.reset_mock()

        mock_backend.ask_gpt(exc_info, stream=False, dialog=True)
        assert mock_prepare_req.called_once_with(exc_info)
        assert mock_send_req.called_with(mock_prepare_req.return_value, False)
        assert mock_print_resp.called_with(mock_send_req.return_value, False)

        assert mock_send_req.call_count == 2
        assert mock_print_resp.call_count == 2
        assert mock_print.called
