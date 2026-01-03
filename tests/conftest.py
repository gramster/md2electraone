"""Pytest configuration and shared fixtures."""
import json
import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Return the path to the fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def load_json():
    """Factory fixture to load JSON files."""
    def _load(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return _load


@pytest.fixture
def load_md():
    """Factory fixture to load Markdown files."""
    def _load(filepath):
        with open(filepath, 'r') as f:
            return f.read()
    return _load
