"""MCP server for Fedora Bodhi."""
import argparse
from fastmcp import FastMCP
from .client import BodhiClient


# Initialize FastMCP server
mcp = FastMCP("Bodhi MCP Server")
bodhi_client = BodhiClient()


@mcp.tool()
async def list_updates(
    user: str | None = None,
    packages: str | None = None,
    status: str | None = None,
    releases: str | None = None,
    rows_per_page: int = 20,
) -> str:
    """
    List Bodhi updates with optional filters.
    
    Args:
        user: Filter by username
        packages: Filter by package name
        status: Filter by status (pending, testing, stable, obsolete, unpushed)
        releases: Filter by release (e.g., F40, F41)
        rows_per_page: Number of results (default: 20, max: 100)
    """
    result = await bodhi_client.get_updates(
        user=user,
        packages=packages,
        status=status,
        releases=releases,
        rows_per_page=min(rows_per_page, 100),
    )
    
    updates = result.get("updates", [])
    total = result.get("total", 0)
    
    response = f"Found {total} total updates. Showing {len(updates)} results:\n\n"
    
    for update in updates:
        response += f"**{update.get('alias')}**\n"
        response += f"  Title: {update.get('title')}\n"
        response += f"  Status: {update.get('status')}\n"
        response += f"  Karma: {update.get('karma', 0)}\n"
        if update.get('date_submitted'):
            response += f"  Submitted: {update.get('date_submitted')}\n"
        response += "\n"
    
    return response


@mcp.tool()
async def get_update(update_id: str) -> str:
    """
    Get details for a specific update by ID.
    
    Args:
        update_id: Update ID (e.g., FEDORA-2024-abc123)
    """
    result = await bodhi_client.get_update(update_id)
    update = result.get("update", {})
    
    response = f"**{update.get('alias')}**\n\n"
    response += f"Title: {update.get('title')}\n"
    response += f"Status: {update.get('status')}\n"
    response += f"Type: {update.get('type')}\n"
    response += f"Karma: {update.get('karma', 0)}\n"
    response += f"Submitted: {update.get('date_submitted')}\n"
    
    if update.get('notes'):
        response += f"\nNotes:\n{update.get('notes')}\n"
    
    if update.get('bugs'):
        response += f"\nBugs: {', '.join([str(b.get('bug_id')) for b in update.get('bugs', [])])}\n"
    
    return response


@mcp.tool()
async def list_releases() -> str:
    """List all Fedora releases."""
    result = await bodhi_client.get_releases()
    releases = result.get("releases", [])
    
    response = f"Found {len(releases)} releases:\n\n"
    
    for release in releases:
        response += f"**{release.get('name')}** - {release.get('state')}\n"
        if release.get('long_name'):
            response += f"  {release.get('long_name')}\n"
    
    return response


@mcp.tool()
async def get_comments(update_id: str) -> str:
    """
    Get comments for a specific update.

    Args:
        update_id: Update ID (e.g., FEDORA-2024-abc123)
    """
    result = await bodhi_client.get_comments(update_id)
    comments = result.get("comments", [])

    if not comments:
        return f"No comments found for update {update_id}"

    response = f"Found {len(comments)} comment(s) for {update_id}:\n\n"

    for comment in comments:
        user = comment.get("user", {}).get("name", "Unknown")
        timestamp = comment.get("timestamp", "")
        text = comment.get("text", "")
        karma = comment.get("karma", 0)

        response += f"**{user}** (karma: {karma:+d}) - {timestamp}\n"
        response += f"{text}\n\n"

    return response


def main():
    """Run the MCP server."""
    parser = argparse.ArgumentParser(description="Bodhi MCP Server")
    parser.add_argument("--bodhi-server", default="https://bodhi.fedoraproject.org",
                       help="Bodhi server URL")
    parser.add_argument("--host", default="127.0.0.1",
                       help="Host to listen on")
    parser.add_argument("--port", type=int, default=8801,
                       help="Port to listen on")
    args = parser.parse_args()
    
    global bodhi_client
    bodhi_client = BodhiClient(base_url=args.bodhi_server)
    
    # Run the server
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
