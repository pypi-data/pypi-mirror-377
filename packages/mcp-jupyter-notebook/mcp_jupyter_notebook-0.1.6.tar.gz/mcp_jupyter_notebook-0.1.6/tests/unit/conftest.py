import pytest
from unittest.mock import AsyncMock, MagicMock

class DummyServer:
    """A dummy server to capture registered tools."""
    def __init__(self):
        self.tools = {}
    def tool(self, name=None, **kwargs):
        def decorator(fn):
            self.tools[name] = fn
            return fn
        return decorator

@pytest.fixture
def dummy_server():
    """Fixture for a dummy server to capture tool registration."""
    return DummyServer()

@pytest.fixture
def mock_session():
    """Fixture for a mock NotebookSession with async methods."""
    session = MagicMock()
    session.is_connected = AsyncMock(return_value=True)
    session.start = AsyncMock()
    session.run_markdown = AsyncMock(return_value=42)
    session.kernel = MagicMock()
    session.kernel.is_alive = AsyncMock(return_value=True)
    return session
