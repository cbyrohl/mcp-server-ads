"""Static resource listing all ADS searchable/returnable fields."""

from mcp_server_ads.server import mcp

FIELDS_REFERENCE = """\
# ADS Searchable Fields

## Common Fields
| Field | Searchable | Description |
|-------|-----------|-------------|
| `bibcode` | Yes | ADS bibcode identifier |
| `title` | Yes | Paper title |
| `author` | Yes | Author names (Last, First) |
| `first_author` | Yes | First author |
| `year` | Yes | Publication year |
| `pubdate` | Yes | Publication date (YYYY-MM-DD) |
| `pub` | Yes | Publication name |
| `abstract` | Yes | Abstract text |
| `keyword` | Yes | Keywords |
| `doi` | Yes | Digital Object Identifier |
| `arxiv_class` | Yes | arXiv category |
| `orcid` | Yes | Author ORCID |

## Citation/Reference Fields
| Field | Searchable | Description |
|-------|-----------|-------------|
| `citation_count` | Sort only | Number of citations |
| `citation` | Yes | Bibcodes that cite this paper |
| `reference` | Yes | Bibcodes this paper cites |
| `read_count` | Sort only | Recent read count |

## Full-text & Properties
| Field | Searchable | Description |
|-------|-----------|-------------|
| `full` | Yes | Full-text search |
| `body` | Yes | Body of the article |
| `ack` | Yes | Acknowledgements |
| `property` | Yes | Paper properties (refereed, openaccess, etc.) |
| `doctype` | Yes | Document type (article, inproceedings, etc.) |
| `database` | Yes | Database (astronomy, physics, general) |

## Identifiers
| Field | Searchable | Description |
|-------|-----------|-------------|
| `identifier` | Yes | Any identifier (bibcode, DOI, arXiv ID) |
| `alternate_bibcode` | Yes | Alternate bibcodes |
| `arXiv` | No (return only) | arXiv identifier |

## Returnabe Metadata Fields
| Field | Description |
|-------|-------------|
| `aff` | Author affiliations |
| `aff_canonical` | Canonical affiliations |
| `volume` | Journal volume |
| `issue` | Journal issue |
| `page` | Page numbers |
| `links_data` | Available links |
| `esources` | Electronic sources |
| `data` | Data links |
| `citation_count_norm` | Normalized citation count |
| `date` | Publication date |
| `entry_date` | Entry date in ADS |

## Functional Operators
- `citations(query)` — papers that cite results of query
- `references(query)` — papers referenced by results of query
- `trending(query)` — trending papers matching query
- `reviews(query)` — review papers matching query
- `useful(query)` — useful papers matching query
- `similar(query)` — similar papers matching query
"""


@mcp.resource("ads://fields")
def get_fields() -> str:
    """Complete reference of ADS searchable and returnable fields."""
    return FIELDS_REFERENCE
