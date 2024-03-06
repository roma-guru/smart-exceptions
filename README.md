# smart-exceptions
Better Python Stacktraces with power of AI.
Now your problems are solved at the same moment they're arised!

## Installation

```console
pip install git+https://github.com/roma-guru/smart-exceptions
```

## Usage

```python
import smart_exceptions as se
se.install("your-openai-token")
```
You can provide token explicitly or implicitly via $OPENAI\_TOKEN.

## TODO
1. Colors!
2. Better prompt (ask for markdown and sections)
3. Markdown highlighting
4. Probably other GPTs: Bard, Yandex
5. Localization
6. Ipython/debug console support
