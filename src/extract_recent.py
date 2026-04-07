"""Extract the last two weeks of COT data from each CFTC and ICE file.

Reads all CSV files from the downloads directory, filters to the two most
recent reporting dates in each file, and writes the results to a separate
recent_reports directory.
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIRECTORY = ROOT_DIR / "downloads"
OUTPUT_DIRECTORY = ROOT_DIR / "recent_reports"

CFTC_DATE_COLUMN = "report_date_as_yyyy_mm_dd"
ICE_DATE_COLUMN = "As_of_Date_Form_MM/DD/YYYY"


def extract_last_two_weeks(
    dataframe: pd.DataFrame, date_column: str
) -> pd.DataFrame:
    """Return rows from the two most recent report dates.

    Args:
        dataframe: Input data containing a date column.
        date_column: Name of the column containing report dates.

    Returns:
        Filtered DataFrame containing only rows from the two most
        recent unique reporting dates.
    """
    parsed_dates = pd.to_datetime(dataframe[date_column], format="mixed")
    most_recent_dates = parsed_dates.drop_duplicates().nlargest(2)
    return dataframe[parsed_dates.isin(most_recent_dates)].copy()


def main() -> None:
    """Extract recent reports from all CFTC and ICE CSV files."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    OUTPUT_DIRECTORY.mkdir(parents=True, exist_ok=True)

    cftc_directory = DOWNLOADS_DIRECTORY / "cftc"
    for csv_path in sorted(cftc_directory.glob("*.csv")):
        logger.info(f"Processing {csv_path.name}...")
        full_data = pd.read_csv(csv_path, low_memory=False)
        recent_data = extract_last_two_weeks(full_data, CFTC_DATE_COLUMN)
        output_path = OUTPUT_DIRECTORY / csv_path.name
        recent_data.to_csv(output_path, index=False)
        logger.info(
            f"  -> {len(recent_data)} rows written to {output_path.name}"
        )

    ice_directory = DOWNLOADS_DIRECTORY / "ice"
    for csv_path in sorted(ice_directory.glob("*.csv")):
        logger.info(f"Processing {csv_path.name}...")
        full_data = pd.read_csv(csv_path, low_memory=False)
        if ICE_DATE_COLUMN in full_data.columns:
            date_column = ICE_DATE_COLUMN
        elif "Date" in full_data.columns:
            date_column = "Date"
        else:
            logger.warning(
                f"  -> Skipping {csv_path.name}: no recognized date column"
            )
            continue
        recent_data = extract_last_two_weeks(full_data, date_column)
        output_path = OUTPUT_DIRECTORY / csv_path.name
        recent_data.to_csv(output_path, index=False)
        logger.info(
            f"  -> {len(recent_data)} rows written to {output_path.name}"
        )

    logger.info(f"Done. All recent reports saved to {OUTPUT_DIRECTORY}/")


if __name__ == "__main__":
    main()
