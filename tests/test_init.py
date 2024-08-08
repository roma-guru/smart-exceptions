import sys
from unittest.mock import patch, MagicMock, sentinel

import smart_exceptions as se
import pytest


@patch("smart_exceptions.get_by_name")
def test_init(mock_get_by_name):
    with patch.dict("os.environ", {}, clear=True), pytest.raises(ValueError):
        se.init()

    mock_backend = MagicMock()
    mock_get_by_name.return_value.return_value = mock_backend
    with patch.dict("os.environ", {"CHATGPT_TOKEN": "tokenhere"}):
        se.init()
    assert se.gpt_backend == mock_backend
    se.gpt_backend = None


@patch("smart_exceptions.detect_env")
def test_install_handler(mock_detect_env, mock_ipython_run):
    mock_detect_env.return_value = "ipython"
    se.install_handler()
    assert (
        mock_ipython_run.return_value.set_custom_exc.call_args[0][1].__name__
        == "smart_ipy_handler"
    )

    mock_detect_env.return_value = "python"
    se.install_handler()
    assert sys.excepthook.__name__ == "smart_handler"


@patch("smart_exceptions.print")
def test_ask(mock_print):
    with pytest.raises(ValueError):
        se.ask()
    se.gpt_backend = MagicMock()
    se.ask()
    assert "WARN" in mock_print.call_args[0][0]

    mock_print.reset_mock()
    with patch("sys.exc_info", return_value=sentinel.exc_info):
        se.ask()
        mock_print.assert_not_called()
        se.gpt_backend.ask_gpt.assert_called_with(
            sentinel.exc_info, stream=True, dialog=True
        )
