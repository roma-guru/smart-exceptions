# smart-exceptions
Better Python Stacktraces with power of AI.
Now your problems are solved at the same moment they're arised!

## Installation
```console
pip install git+https://github.com/roma-guru/smart-exceptions
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

You can provide token explicitly or implicitly via _$OPENAI\_TOKEN_.
Also you can specify proxy explicitly or via _$OPENAI\_PROXY_.
![Example](screenshot.png)

## TODO
- Autoinit from env (*_TOKEN) ???
- TOken counting
- Better pytest support

## Pytest support
Place this in `conftest.py`:
```
import smart_exceptions as se
se.init()


def pytest_exception_interact(node, call, report):
    exc_info = (call.excinfo.type, call.excinfo.value, call.excinfo.traceback[0]._rawentry)
    se.gpt_backend.ask_gpt(exc_info)
```
