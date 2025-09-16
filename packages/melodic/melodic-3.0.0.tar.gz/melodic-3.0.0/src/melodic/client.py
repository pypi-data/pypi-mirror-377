import asyncio
import logging
import types
from pathlib import Path

from .exceptions import SessionNotStartedError
from .models import Track, TrackInfo
from .network import NetworkManager
from .parser import get_artist_url, parse_artist_page, parse_track_page
from .storage import StorageManager

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Melodic:
    """An asynchronous client for fetching lyrical discographies of music artists."""

    def __init__(
        self,
        *,
        storage_path: str | Path | None = None,
        proxies: list[str] | None = None,
        max_concurrent_requests: int = 10,
        max_retry_attempts: int = 5,
        request_delay: float = 3.5,
        user_agent: str | None = None,
        batch_save_size: int = 20,
    ) -> None:
        """Initialize the Melodic client.

        Args:
            storage_path: The file path where the SQLite database will be stored.
            proxies: A list of proxy strings (e.g., "http://user:pass@host:port").
            max_concurrent_requests: The maximum number of concurrent requests.
            max_retry_attempts: The maximum amount of times to retry a failed fetch.
            request_delay: The cooldown period for a proxy after it has been used.
            user_agent: A custom User-Agent string for network requests.
            batch_save_size: The number of songs to accumulate in memory before
                saving them to the database.
        """
        self._network_manager = NetworkManager(
            proxies=proxies,
            max_concurrent_requests=max_concurrent_requests,
            request_delay=request_delay,
            user_agent=user_agent,
        )
        self._storage_manager = StorageManager(storage_path) if storage_path else None
        self._batch_save_size = batch_save_size
        self._max_retry_attempts = max_retry_attempts
        self._in_context = False

        logger.info("Melodic instance has been initialized.")

    async def __aenter__(self) -> "Melodic":
        """Enter async context and intialize resources.

        Returns:
            The initialized Melodic instance.
        """
        await self._network_manager.start()
        if self._storage_manager:
            await self._storage_manager.start()

        self._in_context = True
        logger.debug("Melodic context entered.")
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        """Exit async context and close resources."""
        await self._network_manager.stop()
        if self._storage_manager:
            await self._storage_manager.stop()

        self._in_context = False
        logger.debug("Melodic context exited.")

    async def get_discography(self, artist_name: str) -> dict[str, list[Track]]:
        """Fetch and process the complete lyrical discography for a given artist.

        Args:
            artist_name: The name of the artist.

        Returns:
            A dictionary mapping album names to lists of Track objects.

        Raises:
            SessionNotStartedError: If called outside of async context block.
        """
        if not self._in_context:
            raise SessionNotStartedError(
                "Class resources not initialized. Use an async with block."
            )

        logger.info("Fetching discography for %s", artist_name)
        original_artist_name = artist_name

        artist_url = get_artist_url(artist_name)
        artist_page_html = await self._network_manager.get(artist_url)
        artist_name, track_infos = parse_artist_page(artist_page_html)
        logger.debug("Offical name for %s is %s", original_artist_name, artist_name)

        track_count = len(track_infos)
        tasks = [
            asyncio.create_task(self._fetch_track_lyrics(artist_name, track_info))
            for track_info in track_infos
        ]
        all_tracks = []

        # Process tasks in chunks to save progress periodically
        for i in range(0, len(tasks), self._batch_save_size):
            chunk_tasks = tasks[i : i + self._batch_save_size]
            logger.info(
                "Processing track batch %d-%d of %d...",
                i + 1,
                min(i + self._batch_save_size, len(tasks)),
                len(tasks),
            )
            results = await asyncio.gather(*chunk_tasks, return_exceptions=True)

            chunk_tracks = [track for track in results if isinstance(track, Track)]
            all_tracks.extend(chunk_tracks)

            if self._storage_manager and chunk_tracks:
                await self._storage_manager.save_tracks(chunk_tracks)

        discography: dict[str, list[Track]] = {}
        for track in all_tracks:
            discography.setdefault(track.album_title, []).append(track)

        logger.info(
            "Successfully fetched %d/%d track lyrics for %s.",
            len(all_tracks),
            track_count,
            artist_name,
        )
        return discography

    async def _fetch_track_lyrics(
        self, artist_name: str, track_info: TrackInfo
    ) -> Track | None:
        """Fetch, parse, and create a Track object.

        Args:
            artist_name: The name of the artist.
            track_info: A TrackInfo to get the lyrics for.

        Returns:
            A Track object if successful, otherwise None.
        """
        for i in range(self._max_retry_attempts):
            try:
                track_html = await self._network_manager.get(track_info.url)
                lyrics = parse_track_page(track_html)

                if not lyrics:
                    logger.warning(
                        "Could not find lyrics for %s on %s. Retrying %s/%s",
                        track_info.track_title,
                        track_info.url,
                        i + 1,
                        self._max_retry_attempts,
                    )
                return Track(
                    artist_name=artist_name,
                    album_title=track_info.album_title,
                    track_title=track_info.track_title,
                    lyrics=lyrics,
                    url=track_info.url,
                )
            except Exception as e:
                logger.warning(
                    "Failed to fetch lyrics for %s. Reason: %s. Retrying %s/%s",
                    track_info.track_title,
                    e,
                    i + 1,
                    self._max_retry_attempts,
                )

        return None
