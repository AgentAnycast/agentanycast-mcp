"""Basic smoke tests for agentanycast-mcp package."""

from __future__ import annotations


def test_import():
    """Verify the package is importable and exposes main()."""
    from agentanycast_mcp import main

    assert callable(main)


def test_main_help(capsys):
    """Verify --help exits cleanly."""
    import pytest

    with pytest.raises(SystemExit) as exc_info:
        from agentanycast_mcp import main

        main(["--help"])
    assert exc_info.value.code == 0
