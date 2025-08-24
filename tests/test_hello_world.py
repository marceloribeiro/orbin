"""
Tests for the orbin package.
"""

import sys
import io
from contextlib import redirect_stdout

import pytest

from orbin.helpers.hello_world_helper import (
    hello_world,
    hello_world_with_name,
    get_hello_world_message
)


class TestHelloWorldHelper:
    """Test cases for hello_world_helper module."""

    def test_hello_world(self):
        """Test hello_world function prints correctly."""
        # Capture stdout
        f = io.StringIO()
        with redirect_stdout(f):
            hello_world()
        output = f.getvalue().strip()
        assert output == "hello world"

    def test_hello_world_with_name_default(self):
        """Test hello_world_with_name with default parameter."""
        f = io.StringIO()
        with redirect_stdout(f):
            hello_world_with_name()
        output = f.getvalue().strip()
        assert output == "hello World"

    def test_hello_world_with_name_custom(self):
        """Test hello_world_with_name with custom name."""
        f = io.StringIO()
        with redirect_stdout(f):
            hello_world_with_name("Alice")
        output = f.getvalue().strip()
        assert output == "hello Alice"

    def test_get_hello_world_message(self):
        """Test get_hello_world_message returns correct string."""
        result = get_hello_world_message()
        assert result == "hello world"
        assert isinstance(result, str)


class TestPackageImports:
    """Test package import functionality."""

    def test_import_from_main_package(self):
        """Test importing functions from main package."""
        from orbin import hello_world, hello_world_with_name, get_hello_world_message
        
        # Test that functions are callable
        assert callable(hello_world)
        assert callable(hello_world_with_name)
        assert callable(get_hello_world_message)

    def test_import_from_helpers(self):
        """Test importing from helpers submodule."""
        from orbin.helpers import hello_world, hello_world_with_name, get_hello_world_message
        
        # Test that functions are callable
        assert callable(hello_world)
        assert callable(hello_world_with_name)
        assert callable(get_hello_world_message)

    def test_package_version(self):
        """Test package version is accessible."""
        import orbin
        assert hasattr(orbin, '__version__')
        assert isinstance(orbin.__version__, str)
        assert orbin.__version__ == "0.1.0"
