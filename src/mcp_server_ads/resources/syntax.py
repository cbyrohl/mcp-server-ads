"""Static resource with ADS query syntax quick-reference."""

from mcp_server_ads.server import mcp

SYNTAX_GUIDE = """\
# ADS Query Syntax Quick Reference

## Field-Qualified Searches
- `author:"Einstein, A"` — search by author
- `first_author:"Hawking"` — first author only
- `title:"dark matter"` — search in title
- `abs:"gravitational waves"` — search in abstract
- `full:"machine learning"` — full-text search
- `year:2020` — exact year
- `year:2018-2023` — year range
- `pubdate:[2020-01 TO 2023-06]` — date range
- `bibcode:2016PhRvL.116f1102A` — exact bibcode
- `doi:"10.1038/s41586-020-2649-2"` — DOI search
- `orcid:0000-0002-1825-0097` — ORCID search
- `arxiv_class:"astro-ph.GA"` — arXiv class

## Boolean Operators
- `dark matter AND galaxies` — both terms required
- `supernova OR "stellar explosion"` — either term
- `galaxies NOT dwarf` — exclude term
- Parentheses for grouping: `(dark matter OR dark energy) AND CMB`

## Wildcards & Proximity
- `planet*` — wildcard (planet, planets, planetary, ...)
- `"dark energy"~3` — proximity: terms within 3 words

## Property Filters
- `property:refereed` — peer-reviewed only
- `property:openaccess` — open access
- `property:nonarticle` — non-article documents
- `doctype:article` — articles only
- `doctype:inproceedings` — conference proceedings
- `database:astronomy` — astronomy database

## Functional Operators
- `citations(author:"Einstein")` — papers citing Einstein's papers
- `references(bibcode:2016PhRvL.116f1102A)` — references in a paper
- `trending(title:"exoplanet")` — trending exoplanet papers
- `reviews(abs:"dark matter")` — review articles
- `useful(bibcode:2016PhRvL.116f1102A)` — related useful papers
- `similar(bibcode:2016PhRvL.116f1102A)` — similar papers

## Sort Options
- `date desc` (default) — newest first
- `date asc` — oldest first
- `citation_count desc` — most cited first
- `read_count desc` — most read first
- `score desc` — relevance

## Examples
```
# Find highly-cited dark matter review papers
property:refereed title:"dark matter" doctype:article year:2015-2025
sort: citation_count desc

# Find recent gravitational wave papers by LIGO authors
author:"LIGO" abs:"gravitational wave" year:2020-2025

# Find papers that cite a specific paper
citations(bibcode:2016PhRvL.116f1102A)
```
"""


@mcp.resource("ads://syntax")
def get_syntax() -> str:
    """ADS query syntax quick-reference with examples."""
    return SYNTAX_GUIDE
