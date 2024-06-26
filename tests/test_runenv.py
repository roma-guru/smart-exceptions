from smart_exceptions.run_env import detect_env


def test_detect_env__ipython(mock_ipython_run):
    assert detect_env() == "ipython"


def test_detect_env__console(mock_console_run):
    assert detect_env() == "console"


def test_detect_env__python():
    assert detect_env() == "python"
