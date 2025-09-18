try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # fallback for Python < 3.11
from pathlib import Path

_prompts = {}


def set_prompt_file(path: str | Path):
    global _prompts
    _prompts = {}
    add_prompt_file(path)


def add_prompt_file(path: str | Path):
    global _prompts
    with open(path, 'rb') as f:
        _prompts.update(tomllib.load(f))


def get_prompt(key, **variables):
    global _prompts
    if variables:
        return _prompts[key].format(**variables)
    else:
        return _prompts[key]
