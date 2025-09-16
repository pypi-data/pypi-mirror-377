import re
import unicodedata

from bs4 import BeautifulSoup
from bs4.element import Tag

from .constants import BASE_URL
from .exceptions import DiscographyNotFoundError, MelodicError
from .models import TrackInfo


def get_artist_url(artist_name: str) -> str:
    """Construct the URL for an artist's page.

    Args:
        artist_name: The name of the artist.

    Returns:
        The full URL for the artist's page.
    """
    cleaned_name = _clean_artist_name(artist_name)
    return f"{BASE_URL}/{cleaned_name[0]}/{cleaned_name}.html"


def _clean_artist_name(name: str) -> str:
    """Normalize an artist's name for the URL path.

    Args:
        name: The raw artist name.

    Returns:
        The URL-safe artist name.

    Raises:
        MelodicError: If the name is empty or becomes empty after cleaning.
    """
    if not name or not name.strip():
        raise MelodicError("Artist name cannot be empty.")

    # Normalize to remove accents (e.g., 'é' -> 'e')
    try:
        normalized = unicodedata.normalize("NFKD", name)
        ascii_name = normalized.encode("ASCII", "ignore").decode("utf-8")
    except Exception as e:
        raise MelodicError(f"Failed to normalize artist name: {name}") from e

    # Perform common substitutions (e.g., Ke$ha -> kesha)
    substituted_name = ascii_name.replace("$", "s")

    # Clean to keep only lowercase letters and numbers
    cleaned = re.sub(r"[^a-z0-9]", "", substituted_name.lower())

    if not cleaned:
        raise MelodicError(f"Cleaning artist name: {name} resulted in an empty string.")

    return cleaned


def parse_artist_page(page_html: str) -> tuple[str, list[TrackInfo]]:
    """Parse an artist's page html to find discography metadata.

    Args:
        page_html: The HTML content of the artist's discography page.

    Returns:
        The confirmed name of the artist name and a list containing TrackInfo
            objects.

    Raises:
        DiscographyNotFoundError: If no track metadata could be found on the
            given page html.
    """
    track_infos = []

    soup = BeautifulSoup(page_html, "lxml")

    # Extract artist name
    artist_name_tag = soup.find("h1")
    artist_name = (
        artist_name_tag.text.replace(" Lyrics", "").strip()
        if artist_name_tag and isinstance(artist_name_tag, Tag)
        else "Unknown Artist"
    )

    # Find all track metadatas
    album_title = "N/A"

    for element in soup.select("div#listAlbum > *"):
        if not isinstance(element, Tag):
            continue

        # Album names are in divs with class "album"
        class_attr = element.get("class")
        classes = class_attr if isinstance(class_attr, list) else []

        if element.name == "div" and "album" in classes:
            album_title_tag = element.find("b")

            if album_title_tag:
                album_title = album_title_tag.text.strip().strip('"')

                # Normalize "other songs" variations to our default
                if album_title.lower().rstrip(":").strip() == "other songs":
                    album_title = "[Other]"
            else:
                album_title = "[Other]"

        # Song links are either <a> tags or inside divs with class "listalbum-item"
        elif element.name == "a" or (
            element.name == "div" and "listalbum-item" in classes
        ):
            anchor = element if element.name == "a" else element.find("a")
            if not anchor or not isinstance(anchor, Tag):
                continue

            href = anchor.get("href")
            if not href or not isinstance(href, str) or not href.startswith("/lyrics"):
                continue

            track_url = f"{BASE_URL}{href.removeprefix('../')}"
            track_title = anchor.text.strip()
            track_infos.append(
                TrackInfo(
                    artist_name=artist_name,
                    album_title=album_title,
                    track_title=track_title,
                    url=track_url,
                )
            )

    if not track_infos:
        raise DiscographyNotFoundError(f"No songs found for: {artist_name}")

    return artist_name, track_infos


def parse_track_page(page_html: str) -> str:
    """Parse the track's page html to extract its lyrics.

    Args:
        page_html: The HTML content of the track's page.

    Returns:
        The lyrics of the associated track.
    """
    soup = BeautifulSoup(page_html, "lxml")

    ringtone_div = soup.find("div", class_="ringtone")
    if not ringtone_div or not isinstance(ringtone_div, Tag):
        return ""

    lyrics_div = ringtone_div.find_next("div")
    if lyrics_div and isinstance(lyrics_div, Tag):
        return lyrics_div.get_text(separator="\n", strip=True)

    return ""
