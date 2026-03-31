"""Download ICE Commitments of Traders data from all available sources.

ICE publishes free weekly COT CSV files across multiple exchanges:

1. ICE Futures Europe (2011+):
   https://www.ice.com/publicdocs/futures/COTHist{YEAR}.csv
   Brent, Gasoil, Cocoa, Coffee, Sugar, Wheat, Dubai

2. EU Financials COT (2024+):
   https://www.ice.com/publicdocs/futures/EUFINCOTHist{YEAR}.csv
   FTSE 100 Index, Long Gilt

3. ICE Futures Abu Dhabi (2023+):
   https://www.ice.com/publicdocs/abu_dhabi/IFADCOTHist{YEAR}.csv
   Murban Crude

4. LIFFE Legacy (single historical file, 2012-2013):
   https://www.ice.com/publicdocs/futures/LIFFE_COT_Hist.csv
   Cocoa, Coffee, Sugar, Wheat
"""

import argparse
import datetime
import logging
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ICE_DATASETS = {
    "europe": {
        "url": "https://www.ice.com/publicdocs/futures/COTHist{year}.csv",
        "first_year": 2011,
        "filename": "ice_cot.csv",
        "description": "ICE Futures Europe (Brent, Gasoil, Cocoa, Coffee, Sugar, Wheat, Dubai)",
    },
    "eu_financials": {
        "url": "https://www.ice.com/publicdocs/futures/EUFINCOTHist{year}.csv",
        "first_year": 2024,
        "filename": "ice_eu_financials_cot.csv",
        "description": "EU Financials COT (FTSE 100, Long Gilt)",
    },
    "abu_dhabi": {
        "url": "https://www.ice.com/publicdocs/abu_dhabi/IFADCOTHist{year}.csv",
        "first_year": 2023,
        "filename": "ice_abu_dhabi_cot.csv",
        "description": "ICE Futures Abu Dhabi (Murban Crude)",
    },
    "liffe": {
        "url": "https://www.ice.com/publicdocs/futures/LIFFE_COT_Hist.csv",
        "first_year": None,  # single file, not yearly
        "filename": "ice_liffe_cot.csv",
        "description": "LIFFE Legacy (Cocoa, Coffee, Sugar, Wheat — 2012-2013)",
    },
}

# Keep for backward compatibility
BASE_URL = ICE_DATASETS["europe"]["url"]
FIRST_YEAR = ICE_DATASETS["europe"]["first_year"]
FILENAME = ICE_DATASETS["europe"]["filename"]


class ICEDownloader:
    def __init__(self, output_dir: Path, dataset: str = "europe"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dataset_info = ICE_DATASETS[dataset]
        self.dataset_name = dataset

    @staticmethod
    def _clean_csv(response: requests.Response) -> pd.DataFrame:
        """Parse an ICE CSV response, handling BOM and encoding quirks."""
        from io import StringIO
        text = response.text.lstrip("\ufeff")
        df = pd.read_csv(StringIO(text), low_memory=False, encoding_errors="replace")
        # Fix column names that still carry BOM artifacts (e.g. "ï»¿Market_and_Exchange_Names")
        df.columns = [c.lstrip("\ufeff").lstrip("ï»¿") for c in df.columns]
        return df

    def _fetch_year(self, year: int) -> pd.DataFrame:
        url = self.dataset_info["url"].format(year=year)
        logger.info(f"Fetching {self.dataset_name} COT data for {year} from {url}")
        response = requests.get(url, timeout=120)
        if response.status_code == 404:
            logger.warning(f"No data for {year} (404)")
            return pd.DataFrame()
        response.raise_for_status()
        df = self._clean_csv(response)
        logger.info(f"  {year}: {len(df)} rows")
        return df

    def _fetch_single_file(self) -> pd.DataFrame:
        """Fetch a dataset that is a single file (not yearly)."""
        url = self.dataset_info["url"]
        logger.info(f"Fetching {self.dataset_name} COT data from {url}")
        response = requests.get(url, timeout=120)
        if response.status_code == 404:
            logger.warning(f"No data at {url} (404)")
            return pd.DataFrame()
        response.raise_for_status()
        df = self._clean_csv(response)
        logger.info(f"  {len(df)} rows")
        return df

    def download_full_history(self) -> pd.DataFrame:
        """Download all COT data for this dataset."""
        if self.dataset_info["first_year"] is None:
            return self._fetch_single_file()
        current_year = datetime.date.today().year
        frames = []
        for year in range(self.dataset_info["first_year"], current_year + 1):
            df = self._fetch_year(year)
            if not df.empty:
                frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def download_since(self, since_year: int) -> pd.DataFrame:
        """Download COT data from a given year to current year."""
        if self.dataset_info["first_year"] is None:
            return self._fetch_single_file()
        current_year = datetime.date.today().year
        frames = []
        for year in range(since_year, current_year + 1):
            df = self._fetch_year(year)
            if not df.empty:
                frames.append(df)
        if not frames:
            return pd.DataFrame()
        return pd.concat(frames, ignore_index=True)

    def save(self, df: pd.DataFrame, filename: str | None = None, merge: bool = False):
        """Save DataFrame to CSV. If merge=True, append and deduplicate."""
        if filename is None:
            filename = self.dataset_info["filename"]
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
    """Auto-detect the latest year on disk and download the delta for all datasets."""
    results = {}
    for name, info in ICE_DATASETS.items():
        filepath = output_dir / info["filename"]
        downloader = ICEDownloader(output_dir=output_dir, dataset=name)

        if info["first_year"] is None:
            # Single-file dataset (LIFFE) — always re-download
            df = downloader.download_full_history()
        else:
            since_year = info["first_year"]
            if filepath.exists():
                date_col = "As_of_Date_Form_MM/DD/YYYY"
                try:
                    existing = pd.read_csv(filepath, usecols=[date_col], low_memory=False)
                    if not existing.empty:
                        latest = pd.to_datetime(existing[date_col], format="mixed").max()
                        since_year = latest.year
                except (ValueError, KeyError):
                    pass
            df = downloader.download_since(since_year)

        if not df.empty:
            downloader.save(df, merge=True)

        latest_date = "—"
        if filepath.exists():
            date_col = "As_of_Date_Form_MM/DD/YYYY"
            try:
                saved = pd.read_csv(filepath, usecols=[date_col], low_memory=False)
                if not saved.empty:
                    latest_date = str(pd.to_datetime(saved[date_col], format="mixed").max().date())
            except (ValueError, KeyError):
                pass

        results[name] = {"new_rows": len(df), "latest_date": latest_date}

    return results


def main():
    parser = argparse.ArgumentParser(description="Download ICE COT data")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=list(ICE_DATASETS.keys()) + ["all"],
        default="all",
        help="Which ICE dataset to download (default: all).",
    )
    parser.add_argument(
        "--since-year",
        type=int,
        default=None,
        help="Download from this year onward (default: dataset's first year).",
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

    datasets = list(ICE_DATASETS.keys()) if args.dataset == "all" else [args.dataset]

    for name in datasets:
        info = ICE_DATASETS[name]
        logger.info(f"=== {info['description']} ===")
        downloader = ICEDownloader(output_dir=output_dir, dataset=name)

        if args.since_year:
            df = downloader.download_since(args.since_year)
        else:
            df = downloader.download_full_history()

        if not df.empty:
            downloader.save(df)
            logger.info(f"Done ({name}).\n")
        else:
            logger.warning(f"No data downloaded ({name}).\n")


if __name__ == "__main__":
    main()
