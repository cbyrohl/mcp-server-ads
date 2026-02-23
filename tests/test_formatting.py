"""Tests for formatting functions."""

from mcp_server_ads.formatting import (
    format_author_network,
    format_citation_helper,
    format_export,
    format_libraries,
    format_library_detail,
    format_library_notes,
    format_metrics,
    format_object_results,
    format_paper_network,
    format_reference_resolve,
    format_resolver_links,
    format_search_results,
)
from tests.conftest import load_fixture


def test_format_search_results():
    data = load_fixture("search_response.json")
    result = format_search_results(data)
    assert "150" in result
    assert "Einstein" in result
    assert "1905AnP" in result
    assert "arXiv:physics/0503066" in result
    assert "10.1002/andp.19053221004" in result


def test_format_search_results_empty():
    result = format_search_results({"response": {"numFound": 0, "docs": []}})
    assert "No results" in result


def test_format_export():
    data = load_fixture("export_response.json")
    result = format_export(data)
    assert "@ARTICLE" in result
    assert "Einstein" in result


def test_format_metrics():
    data = load_fixture("metrics_response.json")
    result = format_metrics(data)
    assert "h-index" in result
    assert "80" in result  # total papers
    assert "35" in result  # h-index


def test_format_libraries():
    data = load_fixture("libraries_response.json")
    result = format_libraries(data["libraries"])
    assert "My Reading List" in result
    assert "Dark Matter" in result
    assert "abc123" in result


def test_format_libraries_empty():
    result = format_libraries([])
    assert "No libraries" in result


def test_format_library_detail():
    data = load_fixture("library_detail_response.json")
    result = format_library_detail(data)
    assert "My Reading List" in result
    assert "1905AnP" in result


def test_format_resolver_links():
    data = load_fixture("resolver_response.json")
    result = format_resolver_links(data)
    assert "arXiv" in result
    assert "Publisher" in result


def test_format_object_results():
    data = load_fixture("objects_response.json")
    result = format_object_results(data)
    assert "simbid" in result


def test_format_citation_helper():
    data = load_fixture("citation_helper_response.json")
    result = format_citation_helper(data)
    assert "2017ApJ" in result
    assert "2.00" in result


def test_format_reference_resolve():
    from pathlib import Path

    text = (Path(__file__).parent / "fixtures" / "reference_response.txt").read_text()
    result = format_reference_resolve(text)
    assert "1905AnP" in result
    assert "Einstein" in result


def test_format_author_network():
    data = load_fixture("author_network_response.json")
    result = format_author_network(data)
    assert "Einstein" in result
    assert "Bohr" in result


def test_format_paper_network():
    data = load_fixture("paper_network_response.json")
    result = format_paper_network(data)
    assert "Gravitational Waves" in result
    assert "Black Holes" in result


def test_format_library_notes():
    notes = [
        {"bibcode": "2020ApJ...123..456A", "content": "Great paper on dark matter"},
        {"bibcode": "2021MNRAS..789..012B", "content": "Follow-up study"},
    ]
    result = format_library_notes(notes)
    assert "2020ApJ...123..456A" in result
    assert "Great paper on dark matter" in result
    assert "2021MNRAS..789..012B" in result


def test_format_library_notes_empty():
    result = format_library_notes([])
    assert "No notes" in result
