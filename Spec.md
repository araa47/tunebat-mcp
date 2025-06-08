# Tunebat MCP Server Specification

## Overview

The Tunebat MCP (Model Context Protocol) Server is a Python-based server that provides AI systems with access to music analysis data from [Tunebat.com](https://tunebat.com), a comprehensive music database containing harmonic analysis for over 70 million songs.

## Project Goals

- Enable AI systems to access detailed music analysis data including BPM, key signatures, and harmonic characteristics
- Provide tools for music discovery, harmonic mixing recommendations, and music theory analysis
- Support music education, DJ workflow optimization, and music production assistance
- Offer both individual track lookup and search capabilities

## Technical Foundation

### Architecture
- **Framework**: [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- **Language**: Python 3.12+
- **Dependency Management**: uv (pyproject.toml)
- **Web Scraping**: Web scraping approach (no official API available)
- **Data Format**: Structured JSON responses

### Current Ecosystem Analysis

**Official API**: ❌ Not available
**Existing Libraries**:
- [TheBrenny/tunebat-api](https://github.com/TheBrenny/tunebat-api) (Node.js, 5 stars)
- [FelixMo42/keyScraping](https://github.com/FelixMo42/keyScraping) (Python, basic scraping)

**Opportunity**: First comprehensive Python MCP server for Tunebat data access.

## Data Structure Analysis

Based on website exploration, Tunebat provides the following data for each track:

### Core Track Information
```json
{
  "artist": "Sabrina Carpenter",
  "title": "Manchild",
  "album": "Single",
  "release_date": "June 05, 2025",
  "explicit": true,
  "duration": "3:34",
  "spotify_id": "42UBPzRMh5yyz0EDPr6fr1"
}
```

### Musical Analysis
```json
{
  "key": "G Major",
  "bpm": 123,
  "camelot": "9B",
  "time_signature": "4/4"
}
```

### Audio Characteristics (0-100 scale)
```json
{
  "popularity": 82,
  "energy": 75,
  "danceability": 68,
  "happiness": 71,
  "acousticness": 23,
  "instrumentalness": 2,
  "liveness": 12,
  "speechiness": 8,
  "loudness": -6.2
}
```

### Harmonic Mixing Data
```json
{
  "recommendations": [
    {
      "type": "harmonic_mixing",
      "tracks": [/* similar track objects */]
    },
    {
      "type": "other_recommendations",
      "tracks": [/* related track objects */]
    }
  ]
}
```

## MCP Server Implementation

### Server Configuration

```python
# Server setup following MCP Python SDK patterns
from mcp.server import Server
from mcp.types import Tool, Resource

server = Server("tunebat-server")
```

### Tools Implementation

#### 1. Search Tool
**Name**: `search_tracks`
**Description**: Search for tracks by artist, song title, or keywords
**Parameters**:
- `query` (string, required): Search query
- `limit` (integer, optional): Number of results (default: 10, max: 50)

**Example Usage**:
```json
{
  "query": "karma police radiohead",
  "limit": 5
}
```

#### 2. Track Info Tool
**Name**: `get_track_info`
**Description**: Get detailed information about a specific track
**Parameters**:
- `track_id` (string, required): Tunebat track identifier or Spotify track ID

**Example Usage**:
```json
{
  "track_id": "42UBPzRMh5yyz0EDPr6fr1"
}
```

#### 3. Advanced Search Tool
**Name**: `search_by_attributes`
**Description**: Search tracks by musical attributes
**Parameters**:
- `key` (string, optional): Musical key (e.g., "G Major", "C# Minor")
- `bpm_min` (integer, optional): Minimum BPM
- `bpm_max` (integer, optional): Maximum BPM
- `camelot` (string, optional): Camelot notation (e.g., "9B", "4A")
- `energy_min` (integer, optional): Minimum energy level (0-100)
- `energy_max` (integer, optional): Maximum energy level (0-100)
- `limit` (integer, optional): Number of results (default: 10)

#### 4. Harmonic Mixing Tool
**Name**: `get_harmonic_recommendations`
**Description**: Get tracks that harmonically mix well with a given track
**Parameters**:
- `track_id` (string, required): Reference track ID
- `mixing_type` (string, optional): "harmonic" | "energy" | "all" (default: "harmonic")
- `limit` (integer, optional): Number of recommendations (default: 20)

#### 5. Key Analysis Tool
**Name**: `analyze_key_compatibility`
**Description**: Analyze harmonic compatibility between tracks or keys
**Parameters**:
- `key1` (string, required): First key or track ID
- `key2` (string, required): Second key or track ID
- `analysis_type` (string, optional): "camelot" | "circle_of_fifths" | "both"

### Resources Implementation

#### 1. Track Database Resource
**URI**: `tunebat://tracks/{track_id}`
**Description**: Cached track information
**MIME Type**: `application/json`

#### 2. Search Results Resource
**URI**: `tunebat://search/{query_hash}`
**Description**: Cached search results
**MIME Type**: `application/json`

## Error Handling

### Rate Limiting
- Implement respectful scraping with delays
- Cache frequently accessed data
- Provide clear error messages for rate limits

### Data Validation
- Validate track IDs and search parameters
- Handle missing or incomplete data gracefully
- Provide fallback responses for network issues

### Error Response Format
```json
{
  "error": "TRACK_NOT_FOUND",
  "message": "Track with ID '12345' was not found",
  "code": 404,
  "details": {
    "track_id": "12345",
    "suggestions": ["Check track ID format", "Try searching by name"]
  }
}
```

## Web Scraping Strategy

### Approach
- Use `requests` + `BeautifulSoup4` for static content
- Implement `Playwright` for JavaScript-rendered content if needed
- Respect robots.txt and implement polite scraping practices

### URL Patterns
- Track pages: `https://tunebat.com/Info/{track-slug}/{spotify-id}`
- Search: `https://tunebat.com/search?q={query}`
- Advanced search: `https://tunebat.com/Advanced`

### Caching Strategy
- Implement Redis or SQLite-based caching
- Cache track data for 24 hours
- Cache search results for 1 hour
- Implement cache invalidation for outdated data

## Development Phases

### Phase 1: Core Foundation
- [ ] Set up MCP server structure with Python SDK
- [ ] Implement basic web scraping for individual tracks
- [ ] Create `get_track_info` tool
- [ ] Add basic error handling and logging

### Phase 2: Search Capabilities
- [ ] Implement track search functionality
- [ ] Add `search_tracks` tool
- [ ] Implement result caching
- [ ] Add pagination support

### Phase 3: Advanced Features
- [ ] Add harmonic mixing recommendations
- [ ] Implement `search_by_attributes` tool
- [ ] Add key compatibility analysis
- [ ] Enhance error handling and edge cases

### Phase 4: Production Ready
- [ ] Add comprehensive testing suite
- [ ] Implement robust rate limiting
- [ ] Add monitoring and health checks
- [ ] Create documentation and examples

## Dependencies

### Core Dependencies
```toml
[dependencies]
mcp = "^1.0.0"
requests = "^2.31.0"
beautifulsoup4 = "^4.12.0"
lxml = "^4.9.0"
pydantic = "^2.0.0"
```

### Optional Dependencies
```toml
[dependencies.optional]
playwright = "^1.40.0"  # For JS-heavy pages
redis = "^5.0.0"        # For production caching
sqlite3 = "*"           # For local caching
```

## Configuration

### Environment Variables
- `TUNEBAT_CACHE_TTL`: Cache time-to-live in seconds (default: 86400)
- `TUNEBAT_REQUEST_DELAY`: Delay between requests in seconds (default: 1.0)
- `TUNEBAT_MAX_RETRIES`: Maximum retry attempts (default: 3)
- `TUNEBAT_USER_AGENT`: Custom user agent string

### Server Configuration
```json
{
  "name": "tunebat-server",
  "version": "1.0.0",
  "description": "MCP server for Tunebat music analysis data",
  "capabilities": {
    "tools": true,
    "resources": true,
    "prompts": false
  }
}
```

## Use Cases

### For DJs
- Find tracks in compatible keys for harmonic mixing
- Analyze BPM and energy levels for set planning
- Discover new tracks with similar characteristics

### For Music Producers
- Analyze popular tracks for arrangement insights
- Find reference tracks in specific keys
- Understand harmonic relationships between songs

### For Music Educators
- Teach key relationships and harmonic theory
- Analyze popular music for educational examples
- Demonstrate Camelot wheel concepts

### For AI Music Applications
- Provide music analysis data for recommendation systems
- Support automatic playlist generation
- Enable music theory-aware AI assistants

## Security and Ethics

### Responsible Scraping
- Follow robots.txt guidelines
- Implement respectful rate limiting
- Provide attribution to Tunebat
- Cache data to minimize server load

### Data Usage
- Only extract publicly available data
- Respect Tunebat's terms of service
- Provide clear attribution in responses
- Don't redistribute copyrighted content

## Future Enhancements

### Potential Features
- Real-time BPM detection integration
- Integration with Spotify Web API for additional metadata
- Support for playlist analysis
- Export capabilities for DJ software
- Integration with other music analysis services

### Scalability Considerations
- Implement distributed caching
- Add support for multiple data sources
- Create plugin architecture for extensibility
- Add support for user authentication

## Contributing Guidelines

### Code Standards
- Follow Python PEP 8 style guidelines
- Use type hints throughout the codebase
- Maintain test coverage above 80%
- Document all public APIs

### Development Setup
```bash
# Clone repository
git clone <repo-url>
cd tunebat-mcp

# Install dependencies with uv
uv sync

# Run development server
uv run python -m tunebat_mcp.server
```

## License and Legal

- MIT License for the MCP server code
- Respect Tunebat's terms of service
- Provide proper attribution
- No commercial redistribution of scraped data

---

*This specification serves as the foundation for building a comprehensive Tunebat MCP server that provides AI systems with rich music analysis capabilities while respecting the source platform and following ethical scraping practices.*
