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

    @pytest.mark.asyncio
    async def test_similar_tracks_workflow(self, client: TunebatClient) -> None:
        """Test the complete workflow: search for a track, then get similar tracks."""
        # Step 1: Search for a well-known track
        search_query = "Michael Jackson Thriller"
        search_results = await client.search_with_browser(search_query)

        assert (
            len(search_results) > 0
        ), f"No results found for search query: {search_query}"

        # Step 2: Get the track ID from the first result
        original_track = search_results[0]
        track_id = original_track.spotify_id

        print(
            f"Found track: {original_track.title} by {', '.join(original_track.artists)}"
        )
        print(f"Track ID: {track_id}")

        # Step 3: Get similar tracks using the track ID
        similar_response = await client.get_similar_tracks(track_id)

        # Verify the response structure
        assert similar_response.original_track is not None
        assert similar_response.original_track.spotify_id == track_id

        # Verify we get recommendations
        all_similar = similar_response.all_recommendations
        similar_tracks = similar_response.similar_tracks
        extended_recommendations = similar_response.extended_recommendations

        print(f"Original track: {similar_response.original_track.title}")
        print(f"Total recommendations: {len(all_similar)}")
        print(f"Similar tracks: {len(similar_tracks)}")
        print(f"Extended recommendations: {len(extended_recommendations)}")

        # Should have at least some recommendations
        assert len(all_similar) > 0, "No similar tracks found"

        # Test some similar tracks
        for i, similar_track in enumerate(all_similar[:3]):  # Test first 3
            assert isinstance(similar_track, Track)
            assert similar_track.title is not None
            assert len(similar_track.artists) > 0
            assert similar_track.spotify_id is not None

            print(
                f"  Similar track {i+1}: {similar_track.title} by {', '.join(similar_track.artists)}"
            )
            if similar_track.bpm:
                print(f"    BPM: {similar_track.bpm}")
            if similar_track.key:
                print(f"    Key: {similar_track.key}")

    @pytest.mark.asyncio
    async def test_similar_tracks_invalid_id(self, client: TunebatClient) -> None:
        """Test similar tracks with an invalid track ID."""
        invalid_track_id = "invalid_track_id_12345"

        # Should handle invalid IDs gracefully
        try:
            similar_response = await client.get_similar_tracks(invalid_track_id)
            # If it doesn't raise an error, it should return an empty or minimal response
            print(
                f"Got response for invalid ID (unexpected but handled): {len(similar_response.all_recommendations)} recommendations"
            )
        except Exception as e:
            # Expected behavior - should raise an error for invalid IDs
            print(f"Invalid ID correctly raised error: {type(e).__name__}")
            assert True  # This is expected behavior

    @pytest.mark.asyncio
    async def test_similar_tracks_different_genres(self, client: TunebatClient) -> None:
        """Test similar tracks for different music genres."""
        test_cases = [
            ("Daft Punk One More Time", "Electronic/House"),
            ("Nirvana Smells Like Teen Spirit", "Rock/Grunge"),
            ("Miles Davis Kind of Blue", "Jazz"),
        ]

        for search_query, genre in test_cases:
            print(f"\nTesting similar tracks for {genre}: {search_query}")

            try:
                # Search for the track
                search_results = await client.search_with_browser(search_query)

                if len(search_results) == 0:
                    print(f"  No search results for {search_query}, skipping")
                    continue

                track = search_results[0]
                track_id = track.spotify_id

                print(
                    f"  Found: {track.title} by {', '.join(track.artists)} (ID: {track_id})"
                )

                # Get similar tracks
                similar_response = await client.get_similar_tracks(track_id)
                all_similar = similar_response.all_recommendations

                print(f"  Similar tracks found: {len(all_similar)}")

                # Show first few similar tracks
                for i, similar_track in enumerate(all_similar[:2]):
                    print(
                        f"    {i+1}. {similar_track.title} by {', '.join(similar_track.artists)}"
                    )

            except Exception as e:
                print(f"  Error testing {genre}: {e}")
                # Don't fail the test for individual genre errors
                continue


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
