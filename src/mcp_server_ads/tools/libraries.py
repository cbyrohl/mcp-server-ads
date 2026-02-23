"""Library management tools (consolidated into 2 tools)."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp import Context
from pydantic import Field

from mcp_server_ads.client import ADSClient
from mcp_server_ads.formatting import (
    format_libraries,
    format_library_detail,
    format_library_notes,
)
from mcp_server_ads.server import mcp


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    tags={"libraries"},
)
async def ads_library(
    action: Annotated[
        Literal["list", "get", "create", "edit", "delete"],
        Field(description="Action to perform on a library"),
    ],
    library_id: Annotated[
        str | None,
        Field(description="Library ID (required for get/edit/delete)"),
    ] = None,
    name: Annotated[
        str | None,
        Field(description="Library name (required for create, optional for edit)"),
    ] = None,
    description: Annotated[
        str | None,
        Field(description="Library description (optional for create/edit)"),
    ] = None,
    public: Annotated[
        bool | None,
        Field(description="Whether library is public (optional for create/edit)"),
    ] = None,
    bibcodes: Annotated[
        list[str] | None,
        Field(description="Initial bibcodes when creating a library"),
    ] = None,
    rows: Annotated[
        int,
        Field(description="Number of results to return. Default: 100", ge=1, le=2000),
    ] = 100,
    start: Annotated[
        int,
        Field(description="Starting index for pagination. Default: 0", ge=0),
    ] = 0,
    ctx: Context | None = None,
) -> str:
    """Manage ADS libraries (saved paper collections).

    Actions:
    - list: List all your libraries
    - get: Get a library's details and bibcodes (requires library_id)
    - create: Create a new library (requires name)
    - edit: Edit library metadata (requires library_id)
    - delete: Permanently delete a library (requires library_id)
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]

    if action == "list":
        data = await client.get(
            "/v1/biblib/libraries",
            params={"rows": rows, "start": start},
        )
        return format_libraries(data.get("libraries", []))

    if action == "get":
        data = await client.get(
            f"/v1/biblib/libraries/{library_id}",
            params={"rows": rows, "start": start},
        )
        return format_library_detail(data)

    if action == "create":
        payload: dict = {"name": name, "description": description or ""}
        if bibcodes:
            payload["bibcode"] = bibcodes
        if public is not None:
            payload["public"] = public
        data = await client.post("/v1/biblib/libraries", json=payload)
        lib_id = data.get("id", "?")
        return f"Library created: **{name}** (ID: `{lib_id}`)"

    if action == "edit":
        payload = {}
        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if public is not None:
            payload["public"] = public
        data = await client.put(
            f"/v1/biblib/documents/{library_id}", json=payload
        )
        return f"Library `{library_id}` updated. {data.get('msg', '')}"

    if action == "delete":
        await client.delete(f"/v1/biblib/documents/{library_id}")
        return f"Library `{library_id}` deleted."

    return f"Unknown action: {action}"


@mcp.tool(
    annotations={"readOnlyHint": False, "destructiveHint": False},
    tags={"libraries"},
)
async def ads_library_documents(
    library_id: Annotated[str, Field(description="Library ID")],
    action: Annotated[
        Literal[
            "add", "remove",
            "union", "intersection", "difference", "copy", "empty",
            "get_notes", "add_note", "edit_note", "delete_note",
        ],
        Field(
            description="Action: add/remove bibcodes, "
            "set operations (union/intersection/difference/copy/empty), "
            "or note management (get_notes/add_note/edit_note/delete_note)"
        ),
    ],
    bibcodes: Annotated[
        list[str] | None,
        Field(description="Bibcodes to add/remove"),
    ] = None,
    libraries: Annotated[
        list[str] | None,
        Field(description="Library IDs for set operations"),
    ] = None,
    bibcode: Annotated[
        str | None,
        Field(description="Single bibcode for note operations"),
    ] = None,
    content: Annotated[
        str | None,
        Field(description="Note content (for add_note/edit_note)"),
    ] = None,
    ctx: Context | None = None,
) -> str:
    """Manage documents and notes within an ADS library.

    Document actions:
    - add/remove: Add or remove bibcodes from the library
    - union/intersection/difference/copy/empty: Set operations with other libraries

    Note actions:
    - get_notes: List all notes in the library
    - add_note/edit_note/delete_note: Manage notes on individual papers
    """
    client: ADSClient = ctx.lifespan_context["ads_client"]

    # Add/remove documents
    if action in ("add", "remove"):
        data = await client.post(
            f"/v1/biblib/documents/{library_id}",
            json={"bibcode": bibcodes or [], "action": action},
        )
        count = data.get("number_added", data.get("number_removed", 0))
        return (
            f"{action.capitalize()}d {count} document(s) "
            f"in library `{library_id}`."
        )

    # Set operations
    if action in ("union", "intersection", "difference", "copy", "empty"):
        data = await client.post(
            f"/v1/biblib/libraries/operations/{library_id}",
            json={"libraries": libraries or [], "action": action},
        )
        lib_name = data.get("name", library_id)
        return (
            f"Operation '{action}' completed on library "
            f"**{lib_name}**. {data.get('description', '')}"
        )

    # Note operations
    if action == "get_notes":
        data = await client.get(f"/v1/biblib/notes/{library_id}")
        return format_library_notes(data)

    if action == "add_note":
        await client.post(
            f"/v1/biblib/notes/{library_id}",
            json={"bibcode": bibcode, "content": content},
        )
        return f"Note added for `{bibcode}` in library `{library_id}`."

    if action == "edit_note":
        await client.put(
            f"/v1/biblib/notes/{library_id}",
            json={"bibcode": bibcode, "content": content},
        )
        return f"Note updated for `{bibcode}` in library `{library_id}`."

    if action == "delete_note":
        await client.delete(
            f"/v1/biblib/notes/{library_id}",
            params={"bibcode": bibcode},
        )
        return f"Note deleted for `{bibcode}` in library `{library_id}`."

    return f"Unknown action: {action}"
