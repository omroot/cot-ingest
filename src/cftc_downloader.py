"""Download CFTC Commitments of Traders data from the public reporting API.

Supports seven datasets: disaggregated, legacy, and TFF, each in futures-only
and combined (futures + delta-adjusted options) variants, plus the
Supplemental/CIT report (futures-only). Data is paginated
at 50,000 records per request and saved as CSV files.
"""

import argparse
import logging
from pathlib import Path

import pandas as pd
import requests

from src.cftc_config import load_cftc_credentials

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent

DATASETS: dict[str, dict[str, str]] = {
    "disaggregated": {
        "id": "72hh-3qpy",
        "filename": "disaggregated_futures_only.csv",
    },
    "disaggregated_combined": {
        "id": "kh3c-gbw2",
        "filename": "disaggregated_combined.csv",
    },
    "legacy": {
        "id": "6dca-aqww",
        "filename": "legacy_futures_only.csv",
    },
    "legacy_combined": {
        "id": "jun7-fc8e",
        "filename": "legacy_combined.csv",
    },
    "tff": {
        "id": "gpe5-46if",
        "filename": "tff_futures_only.csv",
    },
    "tff_combined": {
        "id": "yw9f-hn96",
        "filename": "tff_combined.csv",
    },
    "cit": {
        "id": "4zgm-a668",
        "filename": "cit_futures_only.csv",
    },
}


class CFTCDownloader:
    """Client for the CFTC Public Reporting API (Socrata-based).

    Downloads COT data with automatic pagination, optional API token
    authentication (with fallback to unauthenticated requests), and
    CSV persistence with merge/deduplicate support.
    """

    BASE_URL = "https://publicreporting.cftc.gov/resource/{dataset_id}.json"
    PAGE_SIZE = 50_000

    def __init__(
        self,
        application_token: str,
        output_directory: Path,
        dataset: str = "disaggregated",
    ) -> None:
        """Initialize the CFTC downloader.

        Args:
            application_token: CFTC API application token for authentication.
                If rejected (403), the downloader falls back to unauthenticated.
            output_directory: Directory where CSV files will be saved.
            dataset: Name of the CFTC dataset to download. Must be a key in DATASETS.
        """
        self.application_token = application_token
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.dataset_info = DATASETS[dataset]
        self.dataset_name = dataset
        self.url = self.BASE_URL.format(dataset_id=self.dataset_info["id"])

    def _fetch_page(
        self, offset: int, where_clause: str | None = None
    ) -> list[dict]:
        """Fetch a single page of records from the CFTC API.

        Args:
            offset: Number of records to skip (for pagination).
            where_clause: Optional SoQL WHERE filter expression.

        Returns:
            List of record dictionaries from the API response.
        """
        headers: dict[str, str] = {}
        if self.application_token:
            headers["X-App-Token"] = self.application_token
        parameters = {
            "$limit": self.PAGE_SIZE,
            "$offset": offset,
            "$order": "report_date_as_yyyy_mm_dd ASC",
        }
        if where_clause:
            parameters["$where"] = where_clause

        response = requests.get(
            self.url, headers=headers, params=parameters, timeout=120
        )

        if response.status_code == 403 and self.application_token:
            logger.warning("App token rejected (403). Retrying without token.")
            self.application_token = None
            headers.pop("X-App-Token", None)
            response = requests.get(
                self.url, headers=headers, params=parameters, timeout=120
            )

        response.raise_for_status()
        return response.json()

    def _fetch_all_records(
        self, where_clause: str | None = None
    ) -> pd.DataFrame:
        """Fetch all records by paginating through the API.

        Args:
            where_clause: Optional SoQL WHERE filter expression.

        Returns:
            DataFrame containing all fetched records, or an empty DataFrame
            if no records were returned.
        """
        all_records: list[dict] = []
        offset = 0

        while True:
            logger.info(f"Fetching page at offset {offset}...")
            page_records = self._fetch_page(offset, where_clause)

            if not page_records:
                break

            all_records.extend(page_records)
            logger.info(
                f"Retrieved {len(page_records)} records "
                f"(total: {len(all_records)})"
            )

            if len(page_records) < self.PAGE_SIZE:
                break

            offset += self.PAGE_SIZE

        if not all_records:
            return pd.DataFrame()

        return pd.DataFrame(all_records)

    def download_full_history(self) -> pd.DataFrame:
        """Download the complete history for this dataset (2006+).

        Returns:
            DataFrame with all available records.
        """
        logger.info(
            f"Downloading full CFTC {self.dataset_name} history..."
        )
        records = self._fetch_all_records()
        logger.info(f"Downloaded {len(records)} total records")
        return records

    def download_since(self, since_date: str) -> pd.DataFrame:
        """Download records reported after a given date.

        Args:
            since_date: Cutoff date in YYYY-MM-DD format. Only records with
                report_date_as_yyyy_mm_dd strictly after this date are returned.

        Returns:
            DataFrame with records since the given date.
        """
        where_clause = f"report_date_as_yyyy_mm_dd > '{since_date}'"
        logger.info(
            f"Downloading CFTC {self.dataset_name} data since {since_date}..."
        )
        records = self._fetch_all_records(where_clause)
        logger.info(f"Downloaded {len(records)} records since {since_date}")
        return records

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
            merge: If True and the file already exists, append new rows and
                deduplicate by dropping exact duplicate rows.

        Returns:
            Path to the saved CSV file.
        """
        if filename is None:
            filename = self.dataset_info["filename"]
        filepath = self.output_directory / filename
        if merge and filepath.exists():
            existing_data = pd.read_csv(filepath)
            dataframe = pd.concat(
                [existing_data, dataframe], ignore_index=True
            )
            dataframe = dataframe.drop_duplicates()
            dataframe = dataframe.sort_values(
                "report_date_as_yyyy_mm_dd"
            ).reset_index(drop=True)
        dataframe.to_csv(filepath, index=False)
        logger.info(f"Saved {len(dataframe)} records to {filepath}")
        return filepath


def update_all_datasets(
    output_directory: Path, application_token: str
) -> dict[str, dict[str, object]]:
    """Auto-detect the latest date in each dataset and download new records.

    For each of the six CFTC datasets, reads the existing CSV to find the
    most recent report date, then downloads only records after that date.
    If no existing file is found, downloads the full history.

    Args:
        output_directory: Directory containing (and receiving) CSV files.
        application_token: CFTC API application token.

    Returns:
        Dictionary mapping dataset names to their update results, each
        containing 'new_rows' (int) and 'latest_date' (str).
    """
    results: dict[str, dict[str, object]] = {}
    for dataset_name, dataset_info in DATASETS.items():
        filepath = output_directory / dataset_info["filename"]

        since_date: str | None = None
        if filepath.exists():
            existing_data = pd.read_csv(
                filepath, usecols=["report_date_as_yyyy_mm_dd"]
            )
            if not existing_data.empty:
                since_date = existing_data[
                    "report_date_as_yyyy_mm_dd"
                ].max()[:10]

        downloader = CFTCDownloader(
            application_token=application_token,
            output_directory=output_directory,
            dataset=dataset_name,
        )

        if since_date:
            new_data = downloader.download_since(since_date)
            if not new_data.empty:
                downloader.save(new_data, merge=True)
        else:
            new_data = downloader.download_full_history()
            if not new_data.empty:
                downloader.save(new_data)

        latest_date = "—"
        if filepath.exists():
            saved_data = pd.read_csv(
                filepath, usecols=["report_date_as_yyyy_mm_dd"]
            )
            if not saved_data.empty:
                latest_date = saved_data[
                    "report_date_as_yyyy_mm_dd"
                ].max()[:10]

        results[dataset_name] = {
            "new_rows": len(new_data),
            "latest_date": latest_date,
        }

    return results


def main() -> None:
    """CLI entry point for downloading CFTC COT data."""
    parser = argparse.ArgumentParser(description="Download CFTC COT data")
    parser.add_argument(
        "--since",
        type=str,
        default=None,
        help="Download data since this date (YYYY-MM-DD). "
        "If omitted, downloads full history.",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        choices=list(DATASETS.keys()),
        default="disaggregated",
        help="Which CFTC report to download (default: disaggregated).",
    )
    arguments = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    credentials_path = ROOT_DIR / ".env"
    credentials = load_cftc_credentials(credentials_path)
    output_directory = ROOT_DIR / "downloads" / "cftc"

    downloader = CFTCDownloader(
        application_token=credentials["key_id"],
        output_directory=output_directory,
        dataset=arguments.dataset,
    )

    if arguments.since:
        downloaded_data = downloader.download_since(arguments.since)
        downloader.save(downloaded_data, merge=True)
    else:
        downloaded_data = downloader.download_full_history()
        downloader.save(downloaded_data)


if __name__ == "__main__":
    main()
