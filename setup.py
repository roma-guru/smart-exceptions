from setuptools import setup

setup(
        name='smart-exceptions',
        version='0.0.1',
        install_requires=[
            'openai==1.12.0',
            'rich~=13.7',
            'importlib-metadata; python_version>"3.9"',
        ],
)
