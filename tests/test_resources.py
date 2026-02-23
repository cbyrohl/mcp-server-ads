"""Tests for resources."""

from mcp_server_ads.resources.fields import get_fields
from mcp_server_ads.resources.syntax import get_syntax


def test_fields_resource():
    result = get_fields()
    assert "bibcode" in result
    assert "author" in result
    assert "citation_count" in result


def test_syntax_resource():
    result = get_syntax()
    assert "Boolean" in result
    assert "author:" in result
    assert "citations(" in result
