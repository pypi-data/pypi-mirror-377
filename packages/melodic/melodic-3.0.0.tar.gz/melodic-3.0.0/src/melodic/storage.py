import logging
from pathlib import Path

import aiosqlite

from .exceptions import StorageError
from .models import Track

logger = logging.getLogger(__name__)


class StorageManager:
    """A storage backend that saves lyrical discographies to a SQLite database."""

    def __init__(self, storage_path: str | Path) -> None:
        """Initialize the StorageManager backend.

        Args:
            storage_path: The file path where the SQLite database will be stored.
        """
        self._storage_path = Path(storage_path)
        self._connection: aiosqlite.Connection | None = None
        self._initialized = False

    async def start(self) -> None:
        """Open a database connection and configure attributes if required.

        Raises:
            StorageError: If the database connection could not be opened or
                the database could not be initialized.
        """
        if not self._connection:
            try:
                # Connect and optimize DB connection
                self._connection = await aiosqlite.connect(self._storage_path)
                await self._connection.execute("PRAGMA journal_mode = WAL;")
                await self._connection.execute("PRAGMA synchronous = NORMAL;")
                await self._connection.execute("PRAGMA temp_store = MEMORY;")

                if not self._initialized:
                    await self._connection.execute(
                        """
                        CREATE TABLE IF NOT EXISTS tracks (
                            id INTEGER PRIMARY KEY,
                            artist_name TEXT NOT NULL,
                            album_title TEXT NOT NULL,
                            track_title TEXT NOT NULL,
                            lyrics TEXT NOT NULL,
                            url TEXT NOT NULL,
                            UNIQUE(artist_name, track_title)
                        );
                        """
                    )
                    await self._connection.commit()
                    self._initialized = True

                logger.debug("Connection to database opened at: %s", self._storage_path)

            except (aiosqlite.Error, OSError) as e:
                await self.stop()
                raise StorageError(f"Failed to initialize database: {e}") from e

    async def stop(self) -> None:
        """Close the database connection."""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.debug("Database connection closed.")

    async def save_tracks(self, tracks: list[Track]) -> None:
        """Save a list of tracks to the database in a single transaction.

        Args:
            tracks: A list of Track objects to be saved.

        Raises:
            StorageError: If the database connection wasn't established or
                if there was an issue saving tracks to the database.
        """
        if not self._connection:
            raise StorageError("Database connection has not been opened.")

        if not tracks:
            return

        sql = (
            "INSERT OR IGNORE INTO tracks "
            "(artist_name, album_title, track_title, lyrics, url) "
            "VALUES (?, ?, ?, ?, ?)"
        )
        data_to_insert = [
            (
                track.artist_name,
                track.album_title,
                track.track_title,
                track.lyrics,
                track.url,
            )
            for track in tracks
        ]

        try:
            await self._connection.executemany(sql, data_to_insert)
            await self._connection.commit()
            logger.info("Attempted to save %d tracks to the database.", len(tracks))

        except (aiosqlite.Error, OSError) as e:
            raise StorageError(f"Failed to save tracks to database: {e}") from e
