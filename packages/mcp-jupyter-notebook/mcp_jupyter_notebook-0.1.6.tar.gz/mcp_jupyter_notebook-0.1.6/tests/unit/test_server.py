
"""
Unit tests for server.py utilities and entrypoints.
"""
from mcp_jupyter_notebook.server import _parse_headers_env

def test_parse_headers_env_valid(monkeypatch):
    """Test _parse_headers_env parses valid JSON headers from env."""
    monkeypatch.setenv("MCP_JUPYTER_HEADERS_JSON", '{"Authorization": "Bearer token", "X-Test": "yes"}')
    headers = _parse_headers_env()
    assert headers == {"Authorization": "Bearer token", "X-Test": "yes"}

def test_parse_headers_env_invalid_json(monkeypatch):
    """Test _parse_headers_env handles invalid JSON gracefully."""
    monkeypatch.setenv("MCP_JUPYTER_HEADERS_JSON", '{bad json}')
    headers = _parse_headers_env()
    assert headers == {}

def test_parse_headers_env_not_dict(monkeypatch):
    """Test _parse_headers_env handles non-dict JSON gracefully."""
    monkeypatch.setenv("MCP_JUPYTER_HEADERS_JSON", '[1,2,3]')
    headers = _parse_headers_env()
    assert headers == {}

def test_parse_headers_env_missing(monkeypatch):
    """Test _parse_headers_env returns empty dict if env var is missing."""
    monkeypatch.delenv("MCP_JUPYTER_HEADERS_JSON", raising=False)
    headers = _parse_headers_env()
    assert headers == {}
