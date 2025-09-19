"""
kedro_mcp package

Provides a local stdio MCP server with:
- prompt: convert_notebook
- tools: kedro_general_instructions, notebook_to_kedro
"""

from importlib.metadata import PackageNotFoundError, version as _version


def _detect_version() -> str:
    """
    Resolve the installed distribution version.
    Tries common distribution names used for this package.
    Falls back to '0.0.0' in editable/dev mode.
    """
    for dist in ("dimed-mcp", "kedro-mcp"):
        try:
            return _version(dist)
        except PackageNotFoundError:
            continue
    return "0.0.0"


__version__ = _detect_version()

__all__ = ["__version__"]
