"""Atta OpenAI: OpenAI integration for Atta."""

from importlib.metadata import version as get_version

__version__ = get_version("atta-openai")


def test() -> str:
    """Return a test message."""
    return "OpenAI integration ready!"
