import sys


# Jupyter included
def _is_running_in_ipython():
    try:
        get_ipython()
        return True
    except NameError:
        return False


# True for ipython too, so check after
def _is_running_in_console():
    return sys.argv == [""]


def detect_env():
    if _is_running_in_ipython():
        return "ipython"

    if _is_running_in_console():
        return "console"

    return "python"
