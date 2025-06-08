"""Tunebat MCP Server

This server exposes Tunebat API search functionality as MCP tools.
"""

import os
from typing import Any

import click
from fastmcp import FastMCP

from .client import TunebatClient

# Create the main MCP server
mcp = FastMCP("tunebat-mcp")  # type: ignore[misc]

# Initialize the client
client = TunebatClient()


@mcp.resource("tunebat://help")
def get_help() -> str:
    """Get help documentation for using the Tunebat MCP server."""
    return """Tunebat MCP Server Help

This server provides access to music analysis data from Tunebat.com:

- search_tracks: Search for tracks by artist, title, or keywords
- search_tracks_with_retry: Search for tracks with automatic retry on rate limiting
- get_similar_tracks: Get similar tracks for a given Spotify track ID

Returns detailed music analysis data including BPM, key, energy, danceability, and other audio features.

Examples:
- search_tracks("Daft Punk", 10) - Search for Daft Punk tracks
- get_similar_tracks("7MK9eaTSGwGdKA4N7IPdDN", 15) - Get 15 similar tracks to the given track ID
"""


@mcp.tool()
async def search_tracks(query: str, limit: int = 10) -> dict[str, Any]:
    """
    Search for tracks on Tunebat by artist, title, or general query.

    Args:
        query: Search query (artist name, song title, or both)
        limit: Maximum number of results to return (default: 10, max: 100)

    Returns:
        Dictionary containing search results with track analysis data
    """
    tracks = await client.search_with_browser(query)
    tracks = tracks[:limit]

    return {
        "query": query,
        "total_results": len(tracks),
        "tracks": [_track_to_dict(track) for track in tracks],
    }


@mcp.tool()
async def search_tracks_with_retry(
    query: str, limit: int = 10, max_retries: int = 3
) -> dict[str, Any]:
    """
    Search for tracks on Tunebat with automatic retry on rate limiting.

    Args:
        query: Search query (artist name, song title, or both)
        limit: Maximum number of results to return (default: 10, max: 100)
        max_retries: Maximum number of retries (default: 3)

    Returns:
        Dictionary containing search results with track analysis data
    """
    tracks = await client.search_with_retry(query, max_retries)
    tracks = tracks[:limit]

    return {
        "query": query,
        "total_results": len(tracks),
        "tracks": [_track_to_dict(track) for track in tracks],
    }


@mcp.tool()
async def get_similar_tracks(track_id: str, limit: int = 20) -> dict[str, Any]:
    """
    Get similar tracks for a given track ID from Tunebat.

    Args:
        track_id: Spotify track ID (e.g., "7MK9eaTSGwGdKA4N7IPdDN")
        limit: Maximum number of similar tracks to return (default: 20)

    Returns:
        Dictionary containing the original track and similar tracks with analysis data
    """
    try:
        similar_response = await client.get_similar_tracks(track_id)

        # Get all recommendations and limit them
        all_similar = similar_response.all_recommendations[:limit]

        return {
            "track_id": track_id,
            "original_track": _track_to_dict(similar_response.original_track),
            "similar_tracks": [_track_to_dict(track) for track in all_similar],
            "total_similar": len(all_similar),
            "has_more": len(similar_response.all_recommendations) > limit,
        }
    except Exception as e:
        return {
            "error": f"Failed to get similar tracks: {str(e)}",
            "track_id": track_id,
        }


def _track_to_dict(track: Any) -> dict[str, Any]:
    """Convert a Track object to a dictionary."""
    return {
        "spotify_id": track.spotify_id,
        "title": track.title,
        "artists": track.artists,
        "album": track.album,
        "duration_ms": track.duration_ms,
        "bpm": track.bpm,
        "key": track.key,
        "camelot_key": track.camelot_key,
        "energy": track.e,
        "danceability": track.da,
        "happiness": track.h,
        "acousticness": track.ac,
        "instrumentalness": track.i,
        "liveness": track.li,
        "loudness": track.lo,
        "speechiness": track.s,
    }


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport protocol to use (default: stdio)",
)
@click.option("--host", default="127.0.0.1", help="Host to bind to for HTTP transports")
@click.option(
    "--port", default=8000, type=int, help="Port to bind to for HTTP transports"
)
def main(transport: str, host: str, port: int) -> None:
    """Main entry point for the Tunebat MCP Server."""

    # Environment variables override CLI args (for Docker usage)
    final_transport = os.getenv("MCP_TRANSPORT", transport)
    final_host = os.getenv("MCP_HOST") or host
    final_port = int(os.getenv("MCP_PORT", str(port)))

    print(f"Starting Tunebat MCP Server with {final_transport} transport...")

    # Run with appropriate transport
    if final_transport == "stdio":
        mcp.run()
    elif final_transport == "sse":
        print(f"Server running on http://{final_host}:{final_port}/sse")
        mcp.run(transport="sse")
    else:
        # Default fallback
        mcp.run()


if __name__ == "__main__":
    main()
