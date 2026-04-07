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
from io import StringIO
from pathlib import Path

import pandas as pd
import requests

logger = logging.getLogger(__name__)

ICE_DATASETS: dict[str, dict[str, object]] = {
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
        "first_year": None,
        "filename": "ice_liffe_cot.csv",
        "description": "LIFFE Legacy (Cocoa, Coffee, Sugar, Wheat — 2012-2013)",
    },
}

BASE_URL = ICE_DATASETS["europe"]["url"]
FIRST_YEAR = ICE_DATASETS["europe"]["first_year"]
FILENAME = ICE_DATASETS["europe"]["filename"]


class ICEDownloader:
    """Client for downloading ICE Futures COT data from public CSV files.

    Supports multiple ICE exchanges. Each exchange publishes yearly CSV
    files (except LIFFE which is a single historical file). Handles BOM
    and encoding quirks common in ICE CSV files.
    """

    def __init__(self, output_directory: Path, dataset: str = "europe") -> None:
        """Initialize the ICE downloader.

        Args:
            output_directory: Directory where CSV files will be saved.
            dataset: Name of the ICE dataset to download. Must be a key
                in ICE_DATASETS.
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.dataset_info = ICE_DATASETS[dataset]
        self.dataset_name = dataset

    @staticmethod
    def _clean_csv_response(response: requests.Response) -> pd.DataFrame:
        """Parse an ICE CSV response, handling BOM and encoding quirks.

        ICE CSV files sometimes include a UTF-8 BOM at the start and may
        have encoding artifacts in column names. This method strips those
        before parsing.

        Args:
            response: HTTP response containing CSV data.

        Returns:
            Cleaned DataFrame with normalized column names.
        """
        cleaned_text = response.text.lstrip("\ufeff")
        dataframe = pd.read_csv(
            StringIO(cleaned_text), low_memory=False, encoding_errors="replace"
        )
        dataframe.columns = [
            column.lstrip("\ufeff").lstrip("ï»¿") for column in dataframe.columns
        ]
        return dataframe

    def _fetch_year(self, year: int) -> pd.DataFrame:
        """Fetch COT data for a single year.

        Args:
            year: The calendar year to download.

        Returns:
            DataFrame with the year's data, or an empty DataFrame if the
            year is not available (404).
        """
        url = self.dataset_info["url"].format(year=year)
        logger.info(
            f"Fetching {self.dataset_name} COT data for {year} from {url}"
        )
        response = requests.get(url, timeout=120)
        if response.status_code == 404:
            logger.warning(f"No data for {year} (404)")
            return pd.DataFrame()
        response.raise_for_status()
        dataframe = self._clean_csv_response(response)
        logger.info(f"  {year}: {len(dataframe)} rows")
        return dataframe

    def _fetch_single_file(self) -> pd.DataFrame:
        """Fetch a dataset that is a single file (not yearly).

        Used for the LIFFE Legacy dataset which is a single historical
        CSV rather than yearly files.

        Returns:
            DataFrame with all records, or an empty DataFrame if not found.
        """
        url = self.dataset_info["url"]
        logger.info(f"Fetching {self.dataset_name} COT data from {url}")
        response = requests.get(url, timeout=120)
        if response.status_code == 404:
            logger.warning(f"No data at {url} (404)")
            return pd.DataFrame()
        response.raise_for_status()
        dataframe = self._clean_csv_response(response)
        logger.info(f"  {len(dataframe)} rows")
        return dataframe

    def download_full_history(self) -> pd.DataFrame:
        """Download all available COT data for this dataset.

        For yearly datasets, fetches every year from the dataset's first
        year through the current year. For single-file datasets (LIFFE),
        fetches the single file.

        Returns:
            Concatenated DataFrame with all available records.
        """
        if self.dataset_info["first_year"] is None:
            return self._fetch_single_file()
        current_year = datetime.date.today().year
        yearly_frames: list[pd.DataFrame] = []
        for year in range(self.dataset_info["first_year"], current_year + 1):
            year_data = self._fetch_year(year)
            if not year_data.empty:
                yearly_frames.append(year_data)
        if not yearly_frames:
            return pd.DataFrame()
        return pd.concat(yearly_frames, ignore_index=True)

    def download_since(self, since_year: int) -> pd.DataFrame:
        """Download COT data from a given year through the current year.

        Args:
            since_year: First year to include in the download.

        Returns:
            Concatenated DataFrame with records from since_year onward.
        """
        if self.dataset_info["first_year"] is None:
            return self._fetch_single_file()
        current_year = datetime.date.today().year
        yearly_frames: list[pd.DataFrame] = []
        for year in range(since_year, current_year + 1):
            year_data = self._fetch_year(year)
            if not year_data.empty:
                yearly_frames.append(year_data)
        if not yearly_frames:
            return pd.DataFrame()
        return pd.concat(yearly_frames, ignore_index=True)

    def save(
        self,
        dataframe: pd.DataFrame,
        filename: str | None = None,
        merge: bool = False,
    ) -> Path:
        """Save a DataFrame to CSV in the output directory.

        Args:
            dataframe: Data to save.
            filename: Target filename. Defaults to the dataset's configured filename.
            merge: If True and the file already exists, append new rows
                and deduplicate by dropping exact duplicate rows.

        Returns:
            Path to the saved CSV file.
        """
        if filename is None:
            filename = self.dataset_info["filename"]
        filepath = self.output_directory / filename
        if merge and filepath.exists():
            existing_data = pd.read_csv(filepath, low_memory=False)
            dataframe = pd.concat(
                [existing_data, dataframe], ignore_index=True
            )
            dataframe = dataframe.drop_duplicates()
        date_column = "As_of_Date_Form_MM/DD/YYYY"
        if date_column in dataframe.columns:
            dataframe[date_column] = pd.to_datetime(
                dataframe[date_column], format="mixed"
            )
            dataframe = dataframe.sort_values(date_column).reset_index(
                drop=True
            )
        dataframe.to_csv(filepath, index=False)
        logger.info(f"Saved {len(dataframe)} records to {filepath}")
        return filepath


def update_all_ice_datasets(
    output_directory: Path,
) -> dict[str, dict[str, object]]:
    """Auto-detect the latest year on disk and download new data for all ICE datasets.

    For each dataset, reads the existing CSV to find the most recent report
    year, then downloads only from that year onward. Single-file datasets
    (LIFFE) are always re-downloaded entirely.

    Args:
        output_directory: Directory containing (and receiving) CSV files.

    Returns:
        Dictionary mapping dataset names to their update results, each
        containing 'new_rows' (int) and 'latest_date' (str).
    """
    results: dict[str, dict[str, object]] = {}
    for dataset_name, dataset_info in ICE_DATASETS.items():
        filepath = output_directory / dataset_info["filename"]
        downloader = ICEDownloader(
            output_directory=output_directory, dataset=dataset_name
        )

        if dataset_info["first_year"] is None:
            new_data = downloader.download_full_history()
        else:
            since_year = dataset_info["first_year"]
            if filepath.exists():
                date_column = "As_of_Date_Form_MM/DD/YYYY"
                try:
                    existing_data = pd.read_csv(
                        filepath, usecols=[date_column], low_memory=False
                    )
                    if not existing_data.empty:
                        latest_date = pd.to_datetime(
                            existing_data[date_column], format="mixed"
                        ).max()
                        since_year = latest_date.year
                except (ValueError, KeyError):
                    pass
            new_data = downloader.download_since(since_year)

        if not new_data.empty:
            downloader.save(new_data, merge=True)

        latest_date_string = "—"
        if filepath.exists():
            date_column = "As_of_Date_Form_MM/DD/YYYY"
            try:
                saved_data = pd.read_csv(
                    filepath, usecols=[date_column], low_memory=False
                )
                if not saved_data.empty:
                    latest_date_string = str(
                        pd.to_datetime(
                            saved_data[date_column], format="mixed"
                        )
                        .max()
                        .date()
                    )
            except (ValueError, KeyError):
                pass

        results[dataset_name] = {
            "new_rows": len(new_data),
            "latest_date": latest_date_string,
        }

    return results


def main() -> None:
    """CLI entry point for downloading ICE COT data."""
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
    arguments = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    output_directory = (
        Path(arguments.output_dir)
        if arguments.output_dir
        else Path(__file__).resolve().parent.parent / "downloads" / "ice"
    )

    dataset_names = (
        list(ICE_DATASETS.keys())
        if arguments.dataset == "all"
        else [arguments.dataset]
    )

    for dataset_name in dataset_names:
        dataset_info = ICE_DATASETS[dataset_name]
        logger.info(f"=== {dataset_info['description']} ===")
        downloader = ICEDownloader(
            output_directory=output_directory, dataset=dataset_name
        )

        if arguments.since_year:
            downloaded_data = downloader.download_since(arguments.since_year)
        else:
            downloaded_data = downloader.download_full_history()

        if not downloaded_data.empty:
            downloader.save(downloaded_data)
            logger.info(f"Done ({dataset_name}).\n")
        else:
            logger.warning(f"No data downloaded ({dataset_name}).\n")


if __name__ == "__main__":
    main()
