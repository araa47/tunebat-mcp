"""Data models for Tunebat MCP server."""

from typing import Any, Optional

from pydantic import BaseModel, Field


class Track(BaseModel):
    """Model for a Tunebat track."""

    id: str = Field(description="Spotify ID")
    n: str = Field(description="Track title/name")
    as_: list[str] = Field(alias="as", description="List of artists")
    l: Optional[Any] = Field(default=None, description="Unknown field")  # noqa: E741
    an: Optional[str] = Field(default=None, description="Album name")
    rd: Optional[Any] = Field(default=None, description="Unknown field")
    is_: Optional[Any] = Field(default=None, alias="is", description="Unknown field")
    ie: Optional[Any] = Field(default=None, description="Unknown field")
    d: Optional[int] = Field(default=None, description="Duration in milliseconds")
    p: Optional[int] = Field(default=None, description="Popularity (-1 to ?)")
    k: Optional[str] = Field(default=None, description="Musical key")
    kv: Optional[Any] = Field(default=None, description="Unknown field")
    c: Optional[str] = Field(default=None, description="Camelot key")
    b: Optional[int] = Field(default=None, description="BPM (beats per minute)")

    # Audio features (0-1 range)
    ac: Optional[float] = Field(
        default=None, description="Acousticness percentage (0-1)"
    )
    da: Optional[float] = Field(
        default=None, description="Danceability percentage (0-1)"
    )
    e: Optional[float] = Field(default=None, description="Energy percentage (0-1)")
    h: Optional[float] = Field(
        default=None, description="Happiness/valence percentage (0-1)"
    )
    i: Optional[float] = Field(
        default=None, description="Instrumentalness percentage (0-1)"
    )
    li: Optional[float] = Field(default=None, description="Liveness percentage (0-1)")
    lo: Optional[float] = Field(default=None, description="Loudness in dB")
    s: Optional[float] = Field(default=None, description="Speechiness percentage (0-1)")

    # Additional fields
    ci: Optional[list[dict[str, Any]]] = Field(
        default=None, description="Album cover images"
    )
    cr: Optional[Any] = Field(default=None, description="Unknown field")
    r: Optional[list[Any]] = Field(default=None, description="Recommendations")
    er: Optional[list[Any]] = Field(
        default=None, description="Extended recommendations"
    )

    @property
    def title(self) -> str:
        """Get the track title."""
        return self.n

    @property
    def artists(self) -> list[str]:
        """Get the list of artists."""
        return self.as_

    @property
    def album(self) -> Optional[str]:
        """Get the album name."""
        return self.an

    @property
    def duration_ms(self) -> Optional[int]:
        """Get duration in milliseconds."""
        return self.d

    @property
    def bpm(self) -> Optional[int]:
        """Get BPM."""
        return self.b

    @property
    def key(self) -> Optional[str]:
        """Get musical key."""
        return self.k

    @property
    def camelot_key(self) -> Optional[str]:
        """Get Camelot key."""
        return self.c

    @property
    def spotify_id(self) -> str:
        """Get Spotify ID."""
        return self.id


class SimilarTracksResponse(BaseModel):
    """Model for Tunebat similar tracks response."""

    data: Track = Field(description="Original track data with recommendations")

    @property
    def original_track(self) -> Track:
        """Get the original track."""
        return self.data

    @property
    def similar_tracks(self) -> list[Track]:
        """Get the similar tracks from recommendations."""
        recommendations = self.data.r or []
        tracks: list[Track] = []
        for track_data in recommendations:
            if isinstance(track_data, dict):
                try:
                    track = Track.model_validate(track_data)
                    tracks.append(track)
                except Exception:
                    # Skip invalid track data
                    continue
        return tracks

    @property
    def extended_recommendations(self) -> list[Track]:
        """Get the extended recommendations."""
        extended = self.data.er or []
        tracks: list[Track] = []
        for track_data in extended:
            if isinstance(track_data, dict):
                try:
                    track = Track.model_validate(track_data)
                    tracks.append(track)
                except Exception:
                    # Skip invalid track data
                    continue
        return tracks

    @property
    def all_recommendations(self) -> list[Track]:
        """Get all recommendations (similar + extended)."""
        return self.similar_tracks + self.extended_recommendations


class SearchResponse(BaseModel):
    """Model for Tunebat search response."""

    data: dict[str, list[Track]] = Field(description="Response data containing items")

    @property
    def items(self) -> list[Track]:
        """Get the track items from the response."""
        return self.data.get("items", [])


class TunebatError(Exception):
    """Custom exception for Tunebat API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        retry_after: Optional[int] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.retry_after = retry_after
