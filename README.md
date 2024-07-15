# smart-exceptions
Better Python Stacktraces with power of AI.
Now your problems are solved at the same moment they're arised!

## Installation
```console
pip install smart-exceptions
```

## Usage
In file:
```python
import smart_exceptions as se
se.init("your-openai-token")
se.install_handler()
...[code causing exception]...
```
In [debug] console global exception handler is suppressed and have to call GPT explicitly:
```python
>>> import smart_exceptions as se; se.init("your-openai-token")
>>> ...[code causing exception]...
>>> se.ask_gpt()
```

You can provide token explicitly or implicitly via _$OPENAI\_TOKEN_ env variable.
Also you can specify proxy explicitly or via _$OPENAI\_PROXY_.

## Pytest support
Place this in `conftest.py`:
```
import smart_exceptions as se
se.init()


def pytest_exception_interact(node, call, report):
    exc_info = (call.excinfo.type, call.excinfo.value, call.excinfo.traceback[0]._rawentry)
    se.gpt_backend.ask_gpt(exc_info)
```

## Demo
[![Smart Exceptions Demo](https://img.youtube.com/vi/XfaaJW_2RfU/0.jpg)](https://www.youtube.com/watch?v=XfaaJW_2RfU)
