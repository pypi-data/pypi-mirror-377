# Melodic

<p align="center">
  <a href="https://pypi.org/project/melodic/"><img alt="PyPI" src="https://img.shields.io/pypi/v/melodic?color=blue"></a>
  <a href="https://pypi.org/project/melodic/"><img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/melodic"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="License" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
</p>

Melodic is a Python client for fetching artist lyrical discographies. This library provides an asynchronous interface to retrieve complete artist discographies, including album and track metadata including lyrics, with built-in database storage, proxy support, and great error handling.

---

## Features

- **Complete Discography Fetching:** Retrieves full discography metadata and lyrics for any given artist.
- **Asynchronous Interface:** Built with modern `async with` patterns for efficient, safe I/O operations.
- **Database Storage:** Optional built-in storage system for organizing artist, album, and track data.
- **Proxy Support:** Easily pass a list of `HTTP` or `SOCKS` proxies to route requests through.
- **Robust Error Handling:** Comprehensive error handling and logging for reliable operations.
- **Modern Development Tools:** Includes ruff, mypy, pre-commit, and commitizen for high-quality code.

---

## Installation

### From PyPI (Recommended)

```bash
pip install melodic
```

### From Source

You can install melodic by cloning the repository directly or using pre-built wheel files.

**Prerequisites:** This project requires [uv](https://github.com/astral-sh/uv) for dependency management.

#### Option 1: Clone and Build

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/melodic.git
   cd melodic
   ```

2. Install the project and its dependencies:
   ```bash
   uv sync
   ```

#### Option 2: Install from Pre-built Wheels

Pre-built wheel files are automatically generated and attached to each GitHub release. You can download and install them directly:

1. Go to the [GitHub releases page](https://github.com/filming/melodic/releases)
2. Download the `.whl` file from the latest release
3. Install using pip:
   ```bash
   pip install path/to/downloaded/melodic-*.whl

---

## Usage

Here's a basic example of how to use `melodic` to fetch the discography of an artist:

```python
import asyncio
from melodic import Melodic

async def main():
    async with Melodic(storage_path="lyrics.db") as melodic:
        discography = await melodic.get_discography("Taylor Swift")

if __name__ == "__main__":
    asyncio.run(main())
```

This script will fetch the entire lyrical discography for `Taylor Swift` and will return it directly to the calling line in the form of a list of `Track` objects. It will also store the discography into a `lyrics.db` SQLite database if `storage_path` is provided. 

---

## Configuration

Configuration is managed through the `Melodic` client during initialization.

- **`storage_path`**: `str | Path | None` (Default: `None`)
  - The file path where the SQLite database will be stored. If `None`, the database will be created in memory and will not be saved to disk.

- **`proxies`**: `list[str] | None` (Default: `None`)
  - A list of proxy strings (e.g., `["http://user:pass@host:port"]`). If provided, all network requests will be rotated through these proxies.

- **`max_concurrent_requests`**: `int` (Default: `10`)
  - The maximum number of concurrent `aiohttp` requests to make at one time.

- **`max_retry_attempts`**: `int` (Default: 10)
  -  The maximum amount of times to retry a failed fetch.

- **`request_delay`**: `float` (Default: `3.5`)
  - The cooldown period (in seconds) for a proxy after it has been used. This helps prevent rate-limiting. 

- **`user_agent`**: `str | None` (Default: `None`)
  - A custom User-Agent string for network requests. If `None`, a default `aiohttp` User-Agent is used.

- **`batch_save_size`**: `int` (Default: `20`)
  - The number of tracks to accumulate in memory before saving them to the database in a single transaction.

---

## Development

This project uses modern Python development tools:

- **[uv](https://github.com/astral-sh/uv)** for dependency management
- **[ruff](https://github.com/astral-sh/ruff)** for linting and formatting
- **[mypy](https://mypy.readthedocs.io/)** for type checking
- **[pre-commit](https://pre-commit.com/)** for git hooks
- **[commitizen](https://commitizen-tools.github.io/commitizen/)** for conventional commits

### Setting up for development:

1. Clone the repository:
   ```bash
   git clone https://github.com/filming/melodic.git
   cd melodic
   ```

2. Install dependencies (including dev tools):
   ```bash
   uv sync --extra dev
   ```

3. Set up pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

4. Start developing!

---

## Dependencies

All project dependencies are managed via [`pyproject.toml`](pyproject.toml) and use Python 3.10+.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions, bug reports, and feature requests are welcome!
Please open an issue or submit a pull request on [GitHub](https://github.com/filming/melodic).