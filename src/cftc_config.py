"""Load CFTC API credentials from a .env file."""

from pathlib import Path


def load_cftc_credentials(filepath: Path) -> dict[str, str]:
    """Parse a .env file and extract CFTC API credentials.

    Reads key-value pairs from the file, stripping whitespace and quotes.
    Only recognizes CFTC_API_KEY_ID and CFTC_API_KEY_SECRET.

    Args:
        filepath: Path to the .env file containing credentials.

    Returns:
        Dictionary with 'key_id' and 'key_secret' keys. Missing keys are
        omitted rather than set to empty strings.
    """
    credentials: dict[str, str] = {}
    with open(filepath, "r") as env_file:
        for line in env_file:
            stripped_line = line.strip()
            if not stripped_line or "=" not in stripped_line:
                continue
            key, value = stripped_line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key == "CFTC_API_KEY_ID":
                credentials["key_id"] = value
            elif key == "CFTC_API_KEY_SECRET":
                credentials["key_secret"] = value
    return credentials
