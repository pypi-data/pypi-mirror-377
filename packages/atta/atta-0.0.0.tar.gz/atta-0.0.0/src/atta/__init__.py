"""Atta: Attachable AI building blocks."""

from importlib.metadata import version as get_version

__version__ = get_version("atta")


def hello() -> str:
    """Return a greeting message."""
    return "Hello from atta!"
