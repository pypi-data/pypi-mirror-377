"""Basic tests for MultiBrain to ensure pytest runs successfully"""

import pytest
from multibrain._version import __version__


def test_version():
    """Test that version is defined"""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_imports():
    """Test that main modules can be imported"""
    try:
        from multibrain.api import main  # noqa: F401
        from multibrain.api import launch  # noqa: F401
        from multibrain.api.routes import router  # noqa: F401
        from multibrain.api.routes import streaming  # noqa: F401
    except ImportError as e:
        pytest.fail(f"Failed to import module: {e}")


class TestAPIEndpoints:
    """Test basic API endpoint definitions"""

    def test_router_import(self):
        """Test that router can be imported"""
        from multibrain.api.routes.router import router

        assert router is not None

    def test_streaming_router_import(self):
        """Test that streaming router can be imported"""
        from multibrain.api.routes.streaming import router

        assert router is not None
        assert hasattr(router, "prefix")
        assert router.prefix == "/api"
