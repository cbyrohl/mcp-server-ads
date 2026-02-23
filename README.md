# mcp-server-ads

![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)

A powerful [MCP](https://modelcontextprotocol.io/) server for the [NASA Astrophysics Data System (ADS)](https://ui.adsabs.harvard.edu/) — the primary database for astrophysics literature. Search papers, traverse citation graphs forward and backward, export BibTeX, compute metrics, and manage reading lists, all through natural language. Works with Claude Desktop/Code, Cursor, OpenAI Codex, and any MCP-compatible client.

Provides 11 tools, 3 resources, and 3 prompt workflows with token-efficient output designed for LLM consumption.

## Quick Start

### Get an ADS API Token

1. Create a free account at [NASA ADS](https://ui.adsabs.harvard.edu/)
2. Log in and go to [Settings > API Token](https://ui.adsabs.harvard.edu/user/settings/token)
3. Click **Generate a new key** and copy the token

### Prerequisites

- Python 3.11+

### Installation

```bash
# Install from GitHub with uv (recommended)
uv tool install git+https://github.com/cbyrohl/mcp-server-ads

# Or with pip
pip install git+https://github.com/cbyrohl/mcp-server-ads
```

### Claude Desktop

```json
{
  "mcpServers": {
    "ads": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/cbyrohl/mcp-server-ads", "mcp-server-ads"],
      "env": {
        "ADS_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add --scope user mcp-server-ads -e ADS_API_TOKEN=your-api-token-here -- uvx --from git+https://github.com/cbyrohl/mcp-server-ads mcp-server-ads
```

Use `--scope project` instead to share the configuration via `.mcp.json` in your repo, or omit `--scope` for local (current project only).

### Codex CLI

```bash
codex mcp add mcp-server-ads --env ADS_API_TOKEN=your-api-token-here -- uvx --from git+https://github.com/cbyrohl/mcp-server-ads mcp-server-ads
```

This installs to `~/.codex/config.toml` (user-level, available across all projects). For project-scoped config, add the entry to `.codex/config.toml` in your project root instead.

### Running from Source

```bash
git clone https://github.com/cbyrohl/mcp-server-ads.git
cd mcp-server-ads
uv sync

# Run the server
ADS_API_TOKEN=your-token uv run mcp-server-ads
```

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `ADS_API_TOKEN` | Yes | — | API token from ADS |
| `ADS_API_URL` | No | `https://api.adsabs.harvard.edu` | API base URL (override for SciX) |

## Tools (11)

### Search

| Tool | Description |
|------|-------------|
| `ads_search` | Search the ADS database with full query syntax, including `citations()`, `references()`, `similar()`, `trending()`, and `reviews()` operators |
| `ads_bigquery` | Search within a specific set of bibcodes (up to 2000) |

### Export & Metrics

| Tool | Description |
|------|-------------|
| `ads_export` | Export records in 18+ formats (BibTeX, AASTeX, RIS, CSL, etc.) |
| `ads_metrics` | Compute citation metrics (h-index, g-index, citation counts, etc.) |

### Libraries

| Tool | Description |
|------|-------------|
| `ads_library` | Manage libraries: list, get, create, edit, or delete saved paper collections |
| `ads_library_documents` | Manage documents and notes within a library: add/remove papers, set operations (union, intersection, difference, copy, empty), and note CRUD |

### Discovery & Resolution

| Tool | Description |
|------|-------------|
| `ads_resolve_links` | Resolve available links for a paper (full text, data, etc.) |
| `ads_object_search` | Translate astronomical object names to ADS queries (SIMBAD/NED) |
| `ads_citation_helper` | Suggest papers that should be cited alongside a given set |
| `ads_resolve_reference` | Resolve free-text reference strings to ADS bibcodes |

### Network Visualization

| Tool | Description |
|------|-------------|
| `ads_network` | Generate author collaboration or paper citation networks from a set of papers |

## Resources

| URI | Description |
|-----|-------------|
| `ads://fields` | Complete reference of searchable and returnable ADS fields |
| `ads://syntax` | ADS query syntax quick-reference with examples |
| `ads://rate-limits` | Live API rate-limit status |

## Prompts

| Prompt | Description |
|--------|-------------|
| `literature_review` | Multi-step literature review workflow for a research topic |
| `citation_analysis` | Citation network analysis workflow for a set of papers |
| `generate_bibliography` | Generate a formatted bibliography from search or bibcodes |

## Similar Projects

- [prtc/nasa-ads-mcp](https://github.com/prtc/nasa-ads-mcp) — ADS search, metrics, and library management
- [thostetler/scix-mcp](https://github.com/thostetler/scix-mcp) — MCP server for the SciX/ADS API
- [blazickjp/arxiv-mcp-server](https://github.com/blazickjp/arxiv-mcp-server) — MCP server for arXiv paper search and retrieval

This server focuses on broad ADS API coverage, token-efficient output, and integration-tested reliability. Compared to arXiv-based tools, ADS enables forward/backward citation traversal (citations and references of any paper), though it is focused on astrophysics.

## Development

```bash
# Install dev dependencies
uv sync

# Run tests
uv run pytest

# Lint
uv run ruff check src/ tests/

# Run the server locally
ADS_API_TOKEN=your-token uv run mcp-server-ads
```

## License

MIT
