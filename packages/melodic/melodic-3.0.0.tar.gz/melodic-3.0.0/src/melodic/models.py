from dataclasses import dataclass


@dataclass(frozen=True)
class TrackInfo:
    """A temporary object holding a track's metadata."""

    artist_name: str
    album_title: str
    track_title: str
    url: str


@dataclass(frozen=True)
class Track:
    """The final representation of a track, including its lyrics."""

    artist_name: str
    album_title: str
    track_title: str
    lyrics: str
    url: str
