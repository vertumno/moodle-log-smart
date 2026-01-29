"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def fixtures_dir():
    """Provide path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_csv_utf8(tmp_path):
    """Create a sample UTF-8 CSV file for testing."""
    csv_file = tmp_path / "sample_utf8.csv"
    csv_file.write_text("Name,Age,City\nJohn,30,NYC\nJane,25,LA\n", encoding='utf-8')
    return str(csv_file)


@pytest.fixture
def sample_csv_latin1(tmp_path):
    """Create a sample Latin-1 encoded CSV file for testing."""
    csv_file = tmp_path / "sample_latin1.csv"
    content = "Nome;Idade;Cidade\nJoão;30;São Paulo\nMaria;28;Rio de Janeiro\n"
    csv_file.write_bytes(content.encode('latin-1'))
    return str(csv_file)


@pytest.fixture
def sample_csv_tab_delimited(tmp_path):
    """Create a sample tab-delimited CSV file for testing."""
    csv_file = tmp_path / "sample_tab.csv"
    csv_file.write_text("Name\tAge\tCity\nJohn\t30\tNYC\nJane\t25\tLA\n", encoding='utf-8')
    return str(csv_file)
