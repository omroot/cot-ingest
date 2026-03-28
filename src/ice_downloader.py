"""Download ICE Futures Europe Commitments of Traders data.

ICE publishes free weekly COT CSV files (one per year, 2011+) at:
    https://www.ice.com/publicdocs/futures/COTHist{YEAR}.csv

This covers contracts not in the CFTC reports (traded on ICE Futures Europe, London):
    - ICE Brent Crude Futures
    - ICE Gasoil Futures
    - ICE Cocoa Futures
    - ICE Robusta Coffee Futures
    - ICE White Sugar Futures
    - etc.

Data is in disaggregated format (Prod/Merch, Swap, Managed Money, Other Reportables).
"""

import argparse
import datetime
import logging
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://www.ice.com/publicdocs/futures/COTHist{year}.csv"
FIRST_YEAR = 2011
FILENAME = "ice_cot.csv"


class ICEDownloader:
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _fetch_year(self, year: int) -> pd.DataFrame:
        url = BASE_URL.format(year=year)
        logger.info(f"Fetching ICE COT data for {year} from {url}")
        response = requests.get(url, timeout=120)
        if response.status_code == 404:
            logger.warning(f"No data for {year} (404)")
            return pd.DataFrame()
        response.raise_for_status()

        # ICE CSVs may have BOM or encoding quirks
        from io import StringIO
        text = response.text.lstrip("\ufeff")
        df = pd.read_csv(StringIO(text), low_memory=False)
        logger.info(f"  {year}: {len(df)} rows")
        return df

    def download_full_history(self) -> pd.DataFrame:
        """Download all ICE COT data from 2011 to current year."""
        current_year = datetime.date.today().year
        frames = []
        for year in range(FIRST_YEAR, current_year + 1):
            df = self._fetch_year(year)
            if not df.empty:
                frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def download_since(self, since_year: int) -> pd.DataFrame:
        """Download ICE COT data from a given year to current year."""
        current_year = datetime.date.today().year
        frames = []
        for year in range(since_year, current_year + 1):
            df = self._fetch_year(year)
            if not df.empty:
                frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def save(self, df: pd.DataFrame, filename: str = FILENAME, merge: bool = False):
        """Save DataFrame to CSV. If merge=True, append and deduplicate."""
        filepath = self.output_dir / filename
        if merge and filepath.exists():
            existing = pd.read_csv(filepath, low_memory=False)
            df = pd.concat([existing, df], ignore_index=True)
            df = df.drop_duplicates()
        # Sort by date if column exists
        date_col = "As_of_Date_Form_MM/DD/YYYY"
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], format="mixed")
            df = df.sort_values(date_col).reset_index(drop=True)
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(df)} records to {filepath}")
        return filepath


def update_ice(output_dir: Path) -> dict:
    """Auto-detect the latest year on disk and download the delta."""
    filepath = output_dir / FILENAME
    downloader = ICEDownloader(output_dir=output_dir)

    since_year = FIRST_YEAR
    if filepath.exists():
        existing = pd.read_csv(filepath, usecols=["As_of_Date_Form_MM/DD/YYYY"], low_memory=False)
        if not existing.empty:
            latest = pd.to_datetime(existing["As_of_Date_Form_MM/DD/YYYY"], format="mixed").max()
            since_year = latest.year

    df = downloader.download_since(since_year)
    if not df.empty:
        downloader.save(df, merge=True)

    latest_date = "—"
    if filepath.exists():
        saved = pd.read_csv(filepath, usecols=["As_of_Date_Form_MM/DD/YYYY"], low_memory=False)
        if not saved.empty:
            latest_date = str(pd.to_datetime(saved["As_of_Date_Form_MM/DD/YYYY"], format="mixed").max().date())

    return {"new_rows": len(df), "latest_date": latest_date}


def main():
    parser = argparse.ArgumentParser(description="Download ICE Futures Europe COT data")
    parser.add_argument(
        "--since-year",
        type=int,
        default=None,
        help=f"Download from this year onward (default: {FIRST_YEAR}).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: downloads/ice/).",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    output_dir = Path(args.output_dir) if args.output_dir else Path(__file__).resolve().parent.parent / "downloads" / "ice"
    downloader = ICEDownloader(output_dir=output_dir)

    if args.since_year:
        df = downloader.download_since(args.since_year)
    else:
        df = downloader.download_full_history()

    if not df.empty:
        downloader.save(df)
        logger.info("Done.")
    else:
        logger.warning("No data downloaded.")


if __name__ == "__main__":
    main()
