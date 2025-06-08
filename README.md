# 🎵 tunebat-mcp

<div align="center">

*An elegant MCP server for music analysis and discovery*

**Powered by Playwright browser automation | Tunebat data access**

</div>

---

A Model Context Protocol (MCP) server that provides access to Tunebat's music analysis database. This MCP allows AI assistants to search for tracks and retrieve detailed musical analysis data including BPM, key, energy, danceability, and other audio features.

## ✨ Features

- 🔍 **Track Search**: Search for songs by artist, title, or general query
- 📊 **Musical Analysis**: Get detailed audio analysis including:
  - 🥁 BPM (Beats Per Minute)
  - 🎼 Key and Camelot key notation
  - ⚡ Energy, danceability, and happiness metrics
  - 🎸 Acousticness, instrumentalness, and liveness scores
  - 🔊 Loudness and speechiness measurements
- 🎭 **Smart Access**: Uses Playwright browser automation for reliable data retrieval
- 🔄 **Robust**: Built-in retry mechanisms and error handling

## ⚙️ MCP Client Configuration

### 🖱️ Cursor or Claude

```json
{
    "mcpServers": {
        "tunebat-mcp": {
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/araa47/tunebat-mcp.git",
                "tunebat-mcp"
            ]
        }
    }
}
```

## 🚀 Usage Examples

### 🎯 Basic Track Search

**Query**: "What is the BPM of Michael Jackson's Thriller?" 🕺

**Response Example**:
```json
{
  "query": "Michael Jackson Thriller",
  "total_results": 2,
  "tracks": [
    {
      "spotify_id": "2LlQb7Uoj1kKyGhlkBf9aC",
      "title": "Thriller",
      "artists": ["Michael Jackson"],
      "album": "Thriller",
      "duration_ms": 357800,
      "bpm": 118,
      "key": "B Major",
      "camelot_key": "1B",
      "energy": 0.687,
      "danceability": 0.771,
      "happiness": 0.783,
      "acousticness": 0.0318,
      "instrumentalness": 0.000225,
      "liveness": 0.89,
      "loudness": -9.814,
      "speechiness": 0.0693
    }
  ]
}
```

### 🎶 Multi-Artist Search

**Query**: "Find danceable tracks by Daft Punk" 🤖💃

**Sample Log Output**:
```
[INFO] Using Playwright to access Tunebat for: "Daft Punk"
[INFO] Bypassing Cloudflare protection...
[INFO] Found 10 tracks, filtering by danceability > 0.8
[INFO] Top result: "One More Time" - BPM: 123, Danceability: 0.934
```

## 📋 Requirements

This assumes you have [direnv](https://direnv.net/) and [uv](https://github.com/astral-sh/uv) installed 🛠️

Simply run `direnv allow` to setup the environment, you can read the contents of [.envrc](.envrc) to see what it does behind the scenes.

## 🔧 Available Functions

- 🔍 `search_tracks(query, limit)`: Search for tracks with basic functionality
- 🔄 `search_tracks_with_retry(query, limit, max_retries)`: Search with automatic retry on rate limiting

## 🎼 About This Project

This MCP server is built with Python and uses Playwright browser automation to provide reliable access to Tunebat's music analysis data. Perfect for music discovery, DJ preparation, and audio analysis applications.

---

<div align="center">

### 📜 Important Information

This is an community-built tool that accesses publicly available Tunebat data using browser automation.
*Not officially affiliated with Tunebat • Please use responsibly • Respect terms of service*

For official API access or commercial use, consider contacting Tunebat directly.

*Made with ❤️ for music analysis enthusiasts*

</div>
