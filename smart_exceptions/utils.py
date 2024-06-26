import io
import sys
from contextlib import contextmanager


@contextmanager
def redirect_stderr():
    try:
        buffer = io.StringIO()
        sys.stderr = buffer
        yield buffer
    finally:
        sys.stderr = sys.__stderr__
