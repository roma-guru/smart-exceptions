import builtins
import sys
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def mock_ipython_run():
    builtins.get_ipython = MagicMock()
    builtins.__IPYTHON__ = 1
    yield builtins.get_ipython
    del builtins.get_ipython
    del builtins.__IPYTHON__


@pytest.fixture
def mock_console_run():
    with patch("sys.argv", [""]):
        yield
