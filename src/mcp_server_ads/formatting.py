"""Convert ADS API JSON responses to markdown strings."""

from __future__ import annotations

from typing import Any


def _author_list(authors: list[str], max_authors: int = 5) -> str:
    if not authors:
        return "Unknown authors"
    if len(authors) <= max_authors:
        return "; ".join(authors)
    return "; ".join(authors[:max_authors]) + f" et al. ({len(authors)} total)"


def format_paper(doc: dict[str, Any], index: int | None = None) -> str:
    prefix = f"**{index}.** " if index is not None else ""
    title = doc.get("title", ["Untitled"])
    if isinstance(title, list):
        title = title[0] if title else "Untitled"
    authors = _author_list(doc.get("author", []))
    bibcode = doc.get("bibcode", "")
    year = doc.get("year", "?")
    citation_count = doc.get("citation_count", 0)
    pub = doc.get("pub", "")
    abstract = doc.get("abstract", "")
    identifiers = doc.get("identifier", [])

    # Extract arXiv ID and DOI from identifiers
    arxiv_id = ""
    doi = ""
    for ident in identifiers:
        if ident.startswith("arXiv:") and not arxiv_id:
            arxiv_id = ident
        elif ident.startswith("10.") and "/" in ident and not doi:
            doi = ident

    lines = [
        f"{prefix}**{title}**",
        f"  {authors} ({year})",
    ]
    if pub:
        lines.append(f"  *{pub}*")
    ids = f"  Bibcode: `{bibcode}` | Citations: {citation_count}"
    if arxiv_id:
        ids += f" | {arxiv_id}"
    if doi:
        ids += f" | DOI: {doi}"
    lines.append(ids)
    if abstract:
        short = abstract[:300] + "..." if len(abstract) > 300 else abstract
        lines.append(f"  > {short}")
    return "\n".join(lines)


def format_search_results(data: dict[str, Any]) -> str:
    response = data.get("response", {})
    docs = response.get("docs", [])
    num_found = response.get("numFound", 0)

    if not docs:
        return "No results found."

    lines = [f"**Found {num_found:,} results** (showing {len(docs)}):\n"]
    for i, doc in enumerate(docs, 1):
        lines.append(format_paper(doc, index=i))
        lines.append("")
    return "\n".join(lines)


def format_export(data: dict[str, Any]) -> str:
    return data.get("export", data.get("msg", str(data)))


def format_metrics(data: dict[str, Any]) -> str:
    lines = ["## Metrics Summary\n"]

    # The API uses flat keys: "basic stats" and "basic stats refereed"
    basic = data.get("basic stats", {})
    basic_ref = data.get("basic stats refereed", {})
    if basic:
        lines.append("### Basic Statistics")
        lines.append(f"- **Total papers**: {basic.get('number of papers', '?')}")
        lines.append(f"- **Refereed papers**: {basic_ref.get('number of papers', '?')}")
        lines.append(
            f"- **Total reads**: {basic.get('total number of reads', '?')}"
        )
        lines.append(
            f"- **Normalized paper count**: {basic.get('normalized paper count', '?')}"
        )
        lines.append("")

    citation = data.get("citation stats", {})
    citation_ref = data.get("citation stats refereed", {})
    if citation:
        lines.append("### Citation Statistics")
        lines.append(
            f"- **Total citations**: {citation.get('total number of citations', '?')}"
        )
        lines.append(
            f"- **Refereed citations**: "
            f"{citation_ref.get('total number of citations', '?')}"
        )
        lines.append("")

    # The API uses flat keys: "indicators" and "indicators refereed"
    indicators = data.get("indicators", {})
    indicators_ref = data.get("indicators refereed", {})
    if indicators:
        lines.append("### Indicators")
        lines.append(f"- **h-index**: {indicators.get('h', '?')}")
        lines.append(f"- **g-index**: {indicators.get('g', '?')}")
        lines.append(f"- **i10-index**: {indicators.get('i10', '?')}")
        lines.append(f"- **h-index (refereed)**: {indicators_ref.get('h', '?')}")
        lines.append("")

    return "\n".join(lines)


def format_libraries(data: list[dict[str, Any]]) -> str:
    if not data:
        return "No libraries found."
    lines = [f"**{len(data)} libraries:**\n"]
    for lib in data:
        name = lib.get("name", "Untitled")
        desc = lib.get("description", "")
        num = lib.get("num_documents", 0)
        lib_id = lib.get("id", "")
        line = f"- **{name}** ({num} papers) `{lib_id}`"
        if desc:
            line += f"\n  {desc}"
        lines.append(line)
    return "\n".join(lines)


def format_library_detail(data: dict[str, Any]) -> str:
    meta = data.get("metadata", {})
    docs = data.get("documents", [])
    name = meta.get("name", "Untitled")
    desc = meta.get("description", "")
    lines = [f"## {name}"]
    if desc:
        lines.append(f"*{desc}*\n")
    lines.append(f"**{meta.get('num_documents', len(docs))} documents**\n")
    if docs:
        for bib in docs[:50]:
            lines.append(f"- `{bib}`")
        if len(docs) > 50:
            lines.append(f"- ... and {len(docs) - 50} more")
    return "\n".join(lines)


def format_resolver_links(data: dict[str, Any]) -> str:
    links = data.get("links", {}).get("records", [])
    if not links:
        return "No links found."
    lines = ["**Available links:**\n"]
    for link in links:
        title = link.get("title", link.get("type", "Link"))
        url = link.get("url", "")
        lines.append(f"- [{title}]({url})")
    return "\n".join(lines)


def format_object_results(data: dict[str, Any]) -> str:
    query = data.get("query", "")
    if query:
        return f"Translated object query: `{query}`"
    return str(data)


def format_citation_helper(data: dict[str, Any] | list) -> str:
    # The API returns a plain list of suggestions
    if isinstance(data, list):
        suggestions = data
    else:
        suggestions = data.get("new", [])
    if not suggestions:
        return "No citation suggestions found."
    lines = [f"**{len(suggestions)} suggested references:**\n"]
    for i, item in enumerate(suggestions, 1):
        bibcode = item.get("bibcode", "?")
        score = item.get("score", 0)
        title = item.get("title", "")
        author = item.get("author", "")
        line = f"{i}. `{bibcode}` (score: {score:.2f})"
        if title:
            line += f"\n   **{title}**"
        if author:
            line += f"\n   {author}"
        lines.append(line)
    return "\n".join(lines)


def format_reference_resolve(data: str) -> str:
    """Format reference resolution results.

    The API returns plain text lines like:
      1.0 1905AnP...322..891E -- Einstein 1905 Annalen der Physik 17 891
      0.0                     -- Some unresolved reference
    """
    if not data or not data.strip():
        return "Could not resolve reference."
    lines = ["**Resolved references:**\n"]
    for raw_line in data.strip().splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        parts = raw_line.split(" -- ", 1)
        if len(parts) == 2:
            score_bib = parts[0].strip()
            ref_text = parts[1].strip()
            tokens = score_bib.split()
            score = tokens[0] if tokens else "?"
            bibcode = tokens[1] if len(tokens) > 1 else ""
            lines.append(f"- {ref_text}")
            if bibcode:
                lines.append(f"  -> `{bibcode}` (score: {score})")
            else:
                lines.append(f"  -> Not resolved (score: {score})")
        else:
            lines.append(f"- {raw_line}")
    return "\n".join(lines)


def format_author_network(data: dict[str, Any]) -> str:
    d = data.get("data", {})
    if not d:
        return "No author network data."
    root = d.get("root", {})
    name = root.get("name", "Network")
    children = root.get("children", [])
    lines = [f"## Author Network: {name}\n"]
    lines.append(f"**{len(children)} author groups:**\n")
    for group in children[:20]:
        gname = group.get("name", "?")
        size = group.get("size", 0)
        lines.append(f"- **{gname}** (size: {size})")
    if len(children) > 20:
        lines.append(f"- ... and {len(children) - 20} more groups")

    summary = d.get("summary", [])
    if summary:
        lines.append("\n### Summary")
        for item in summary[:10]:
            lines.append(f"- {item}")
    return "\n".join(lines)


def format_paper_network(data: dict[str, Any]) -> str:
    d = data.get("data", {})
    if not d:
        return "No paper network data."
    root = d.get("root", {})
    name = root.get("name", "Network")
    children = root.get("children", [])
    lines = [f"## Paper Network: {name}\n"]
    lines.append(f"**{len(children)} paper groups:**\n")
    for group in children[:20]:
        gname = group.get("name", "?")
        size = group.get("size", 0)
        lines.append(f"- **{gname}** (size: {size})")
    if len(children) > 20:
        lines.append(f"- ... and {len(children) - 20} more groups")

    summary = d.get("summary", [])
    if summary:
        lines.append("\n### Summary")
        for item in summary[:10]:
            lines.append(f"- {item}")
    return "\n".join(lines)


def format_library_notes(data: dict[str, Any] | list | str) -> str:
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        if not data:
            return "No notes found."
        lines = ["**Notes:**\n"]
        for note in data:
            bib = note.get("bibcode", "?")
            content = note.get("content", "")
            lines.append(f"- `{bib}`: {content}")
        return "\n".join(lines)
    return str(data)
