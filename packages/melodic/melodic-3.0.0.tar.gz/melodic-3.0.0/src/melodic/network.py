import asyncio
import logging
import random
import time

import aiohttp
from aiohttp_socks import ProxyConnector
from bs4 import BeautifulSoup

from .constants import DEFAULT_USER_AGENT, HTTP_STATUSES
from .exceptions import (
    ConfigError,
    IPBlockedError,
    NetworkError,
    SessionNotStartedError,
)

logger = logging.getLogger(__name__)
VALID_PROXY_SCHEMES = ("http://", "socks4://", "socks5://")


class NetworkManager:
    """Manage network requests."""

    def __init__(
        self,
        proxies: list[str] | None,
        max_concurrent_requests: int,
        request_delay: float,
        user_agent: str | None,
    ) -> None:
        """Initialize the NetworkManager.

        Args:
            proxies: A list of proxy strings (e.g., "http://user:pass@host:port").
            max_concurrent_requests: The maximum number of concurrent requests.
            request_delay: The cooldown period for a proxy after it has been used.
            user_agent: A custom User-Agent string for network requests.

        Raises:
            ConfigError: If a proxy URL has an invalid format.
        """
        self._request_delay = request_delay
        self._user_agent = user_agent or DEFAULT_USER_AGENT

        if proxies:
            # Validate each proxy format before proceeding
            for proxy in proxies:
                if not proxy.startswith(VALID_PROXY_SCHEMES):
                    raise ConfigError(
                        f"Invalid proxy format, {proxy}. "
                        f"Proxy must start with one of {VALID_PROXY_SCHEMES}."
                    )

        # State for managing statuses of proxies
        self._proxy_cooldowns: dict[str, float] = (
            {p: 0.0 for p in proxies} if proxies else {"Local-IP": 0.0}
        )
        self._dead_proxies: set[str] = set()
        self._proxy_lock = asyncio.Lock()

        # Determine concurrency limit
        num_proxies = len(self._proxy_cooldowns)
        concurrency_limit = min(num_proxies, max_concurrent_requests)
        self._semaphore = asyncio.Semaphore(concurrency_limit)

        self._session: aiohttp.ClientSession | None = None
        self._timeout = aiohttp.ClientTimeout(total=10)

    async def start(self) -> None:
        """Initialize the aiohttp session."""
        if not self._session:
            self._session = aiohttp.ClientSession(
                headers={"User-Agent": self._user_agent}
            )
        logger.debug("NetworkManager has been started.")

    async def stop(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None
        logger.debug("NetworkManager has been stopped.")

    async def _get_available_proxy(self) -> str:
        """Select a proxy that is not on cooldown or marked as dead.

        Returns:
            The URL of an available proxy, or None if not using proxies.

        Raises:
            NetworkError: If all available proxies are marked as dead.
        """
        async with self._proxy_lock:
            while True:
                # Get all available proxies based on when they were last used
                now = time.monotonic()

                available_proxies = [
                    p
                    for p, last_used in self._proxy_cooldowns.items()
                    if p not in self._dead_proxies
                    and (now - last_used) >= self._request_delay
                ]

                if available_proxies:
                    selected_proxy = random.choice(available_proxies)
                    self._proxy_cooldowns[selected_proxy] = now
                    return selected_proxy

                # Check if all proxies (even those on cooldown) are dead
                if len(self._dead_proxies) == len(self._proxy_cooldowns):
                    raise NetworkError("All available proxies have failed.")

                # If no proxies are available right now, wait and retry
                logger.debug("All live proxies are on cooldown, waiting to select one.")
                await asyncio.sleep(1)

    async def get(self, url: str) -> str:
        """Perform an asynchronous GET request for the given URL.

        Args:
            url: The URL to fetch.

        Returns:
            The text content of the HTTP response.

        Raises:
            SessionNotStartedError: If the network session is not active.
        """
        if not self._session:
            raise SessionNotStartedError("Network session was not started.")

        async with self._semaphore:
            proxy_url = await self._get_available_proxy()

            logger.debug("Requested URL %s via %s", url, proxy_url)

            # No proxy or an HTTP/HTTPS proxy. Use the main session.
            if (proxy_url == "Local-IP") or proxy_url.startswith("http"):
                return await self._make_request_and_validate(
                    self._session, url, proxy_url
                )

            # A new session with a SOCKS connector is required.
            else:
                connector = ProxyConnector.from_url(proxy_url)
                async with aiohttp.ClientSession(
                    connector=connector, headers=self._session.headers
                ) as session:
                    return await self._make_request_and_validate(
                        session, url, proxy_url
                    )

    async def _make_request_and_validate(
        self,
        session: aiohttp.ClientSession,
        url: str,
        proxy_url: str,
    ) -> str:
        """Make a HTTP request and validate the response.

        Args:
            session: The aiohttp client to make a HTTP request with.
            url: The URL to make the HTTP request to.
            proxy_url: The proxy to use for the HTTP request.

        Returns:
            The text content of the HTTP response.

        Raises:
            NetworkError: If attempting to make a request fails.
            IPBlockedError: If an IP has been blocked on the target website.
        """
        try:
            if (proxy_url == "Local-IP") or proxy_url.startswith("http"):
                proxy = None if proxy_url == "Local-IP" else proxy_url

                async with session.get(
                    url, proxy=proxy, timeout=self._timeout
                ) as response:
                    response.raise_for_status()
                    page_html = await response.text()
            else:
                async with session.get(url, timeout=self._timeout) as response:
                    response.raise_for_status()
                    page_html = await response.text()

            page_validity = self._validate_page_access(page_html)
            if not page_validity:
                raise IPBlockedError(f"{proxy_url} has been blocked on {url}")

            return page_html

        except IPBlockedError:
            logger.warning(
                "%s has been blocked on %s. Marking as dead.", proxy_url, url
            )
            async with self._proxy_lock:
                self._dead_proxies.add(proxy_url)
            raise

        except asyncio.TimeoutError as e:
            raise NetworkError(f"Request to {url} timed out") from e

        except (aiohttp.ClientError, aiohttp.ClientResponseError) as e:
            status = getattr(e, "status", None)

            if status == HTTP_STATUSES["NOT_FOUND"]:
                raise NetworkError(f"Page not found at {url}") from e
            elif status == HTTP_STATUSES["FORBIDDEN"]:
                raise IPBlockedError(f"{proxy_url} is forbidden from {url}") from e

            raise NetworkError(
                f"Network request to {url} failed: {e}", status=status
            ) from e

    def _validate_page_access(self, page_html: str) -> bool:
        """Validate whether or not access to requested page was granted.

        Args:
            page_html: The text content of the HTTP response.

        Returns:
            A boolean representing whether access was granted or not.
        """
        soup = BeautifulSoup(page_html, "lxml")
        title_tag = soup.find("title")

        if title_tag:
            title = title_tag.get_text()
            return "request for access" not in title

        return False
