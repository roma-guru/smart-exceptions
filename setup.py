from setuptools import setup

setup(
    name="smart-exceptions",
    version="0.1.0",
    install_requires=[
        "openai==1.12.0",
        "tiktoken==0.7.0",
        "anthropic==0.20.0",
        "groq==0.5.0",
        "rich~=13.7",
        'importlib-metadata; python_version>"3.10"',
    ],
)
