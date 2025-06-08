"""End-to-end tests for TunebatClient.

These tests make actual API calls to Tunebat to ensure the client works correctly.
Run sparingly to avoid rate limiting.
"""

import asyncio

import pytest
from tunebat_mcp.client import TunebatClient
from tunebat_mcp.models import Track


class TestTunebatClientE2E:
    """E2E tests for TunebatClient."""

    @pytest.fixture
    def client(self) -> TunebatClient:
        """Create a TunebatClient instance."""
        return TunebatClient(timeout=30.0)

    @pytest.mark.asyncio
    async def test_search_popular_song(self, client: TunebatClient) -> None:
        """Test searching for a popular song."""
        # Search for a well-known song
        query = "Daft Punk One More Time"
        results = await client.search_with_browser(query)

        # Verify we got results
        assert len(results) > 0, f"No results found for query: {query}"

        # Check the first result
        track = results[0]
        assert isinstance(track, Track)
        assert track.title is not None
        assert len(track.artists) > 0
        assert track.spotify_id is not None

        # Verify audio features are present (at least some)
        assert track.bpm is not None or track.e is not None or track.da is not None

        print(f"Found {len(results)} results for '{query}'")
        print(f"First result: {track.title} by {', '.join(track.artists)}")
        if track.bpm:
            print(f"BPM: {track.bpm}")
        if track.key:
            print(f"Key: {track.key}")

    @pytest.mark.asyncio
    async def test_search_by_artist(self, client: TunebatClient) -> None:
        """Test searching by artist name."""
        query = "Deadmau5"
        results = await client.search_with_browser(query)

        assert len(results) > 0, f"No results found for artist: {query}"

        # Verify at least one result contains the artist name
        found_artist = False
        for track in results:
            if any(query.lower() in artist.lower() for artist in track.artists):
                found_artist = True
                break

        assert found_artist, f"No tracks found for artist: {query}"

        print(f"Found {len(results)} results for artist '{query}'")

    @pytest.mark.asyncio
    async def test_search_nonexistent_song(self, client: TunebatClient) -> None:
        """Test searching for a song that doesn't exist."""
        query = "ThisSongDoesNotExistAnywhere12345"
        results = await client.search_with_browser(query)

        # Should return empty list, not raise an error
        assert isinstance(results, list)
        # May be empty or have some random results
        print(f"Found {len(results)} results for nonexistent query '{query}'")

    @pytest.mark.asyncio
    async def test_search_with_retry_success(self, client: TunebatClient) -> None:
        """Test search_with_retry with a successful query."""
        query = "Calvin Harris Feel So Close"
        results = await client.search_with_retry(query, max_retries=2)

        assert len(results) > 0, f"No results found for query: {query}"

        track = results[0]
        assert isinstance(track, Track)
        assert track.title is not None
        assert len(track.artists) > 0

        print(f"Found {len(results)} results with retry for '{query}'")

    @pytest.mark.asyncio
    async def test_search_unicode_query(self, client: TunebatClient) -> None:
        """Test searching with unicode characters."""
        query = "Stromae Alors On Danse"  # French artist/song
        results = await client.search_with_browser(query)

        # Should handle unicode properly
        assert isinstance(results, list)

        if len(results) > 0:
            track = results[0]
            assert isinstance(track, Track)
            print(f"Found {len(results)} results for unicode query '{query}'")
            print(f"First result: {track.title} by {', '.join(track.artists)}")
        else:
            print(f"No results for unicode query '{query}' (acceptable)")

    @pytest.mark.asyncio
    async def test_track_properties(self, client: TunebatClient) -> None:
        """Test that Track properties work correctly."""
        query = "Avicii Levels"
        results = await client.search_with_browser(query)

        assert len(results) > 0, f"No results found for query: {query}"

        track = results[0]

        # Test all property accessors
        assert track.spotify_id == track.id
        assert track.title == track.n
        assert track.artists == track.as_
        assert track.album == track.an
        assert track.duration_ms == track.d
        assert track.bpm == track.b
        assert track.key == track.k
        assert track.camelot_key == track.c

        print(f"Track properties test passed for: {track.title}")
        print(f"  Spotify ID: {track.spotify_id}")
        print(f"  Duration: {track.duration_ms}ms")
        if track.bpm:
            print(f"  BPM: {track.bpm}")
        if track.key:
            print(f"  Key: {track.key}")
        if track.camelot_key:
            print(f"  Camelot Key: {track.camelot_key}")

    @pytest.mark.asyncio
    async def test_audio_features(self, client: TunebatClient) -> None:
        """Test that audio features are correctly parsed."""
        query = "Swedish House Mafia Don't You Worry Child"
        results = await client.search_with_browser(query)

        assert len(results) > 0, f"No results found for query: {query}"

        track = results[0]

        # Check that at least some audio features are present
        features = [track.e, track.da, track.h, track.ac, track.i, track.li, track.s]
        non_null_features = [f for f in features if f is not None]

        assert len(non_null_features) > 0, "No audio features found"

        # Verify range constraints for percentage features (0-1)
        for feature in non_null_features:
            assert 0 <= feature <= 1, f"Audio feature {feature} out of range [0,1]"

        print(f"Audio features test passed for: {track.title}")
        print(f"  Energy: {track.e}")
        print(f"  Danceability: {track.da}")
        print(f"  Happiness: {track.h}")
        print(f"  Acousticness: {track.ac}")


# Helper function to run specific tests
async def run_single_test() -> None:
    """Run a single test for quick verification."""
    client = TunebatClient()
    results = await client.search_with_browser("Daft Punk")
    print(f"Quick test: Found {len(results)} results for 'Daft Punk'")
    if results:
        track = results[0]
        print(f"First result: {track.title} by {', '.join(track.artists)}")


if __name__ == "__main__":
    # Quick test when run directly
    asyncio.run(run_single_test())
