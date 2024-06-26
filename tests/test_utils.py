import sys

from smart_exceptions.utils import redirect_stderr


def test_redirect_stderr():
    with redirect_stderr() as buffer:
        print("Hello, stderr!", file=sys.stderr)
        assert buffer.getvalue() == "Hello, stderr!\n"
