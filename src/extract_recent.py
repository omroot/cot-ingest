"""Extract the last two weeks of COT data from each CFTC and ICE file."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = ROOT_DIR / "downloads"
OUTPUT_DIR = ROOT_DIR / "recent_reports"

CFTC_DATE_COL = "report_date_as_yyyy_mm_dd"
ICE_DATE_COL = "As_of_Date_Form_MM/DD/YYYY"


def extract_last_two_weeks(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    """Return rows from the two most recent report dates."""
    dates = pd.to_datetime(df[date_col], format="mixed")
    unique_dates = dates.drop_duplicates().nlargest(2)
    return df[dates.isin(unique_dates)].copy()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # CFTC files
    cftc_dir = DOWNLOADS_DIR / "cftc"
    for csv_path in sorted(cftc_dir.glob("*.csv")):
        logger.info(f"Processing {csv_path.name}...")
        df = pd.read_csv(csv_path, low_memory=False)
        recent = extract_last_two_weeks(df, CFTC_DATE_COL)
        out = OUTPUT_DIR / csv_path.name
        recent.to_csv(out, index=False)
        logger.info(f"  -> {len(recent)} rows written to {out.name}")

    # ICE files
    ice_dir = DOWNLOADS_DIR / "ice"
    for csv_path in sorted(ice_dir.glob("*.csv")):
        logger.info(f"Processing {csv_path.name}...")
        df = pd.read_csv(csv_path, low_memory=False)
        # Detect the date column
        if ICE_DATE_COL in df.columns:
            date_col = ICE_DATE_COL
        elif "Date" in df.columns:
            date_col = "Date"
        else:
            logger.warning(f"  -> Skipping {csv_path.name}: no recognized date column")
            continue
        recent = extract_last_two_weeks(df, date_col)
        out = OUTPUT_DIR / csv_path.name
        recent.to_csv(out, index=False)
        logger.info(f"  -> {len(recent)} rows written to {out.name}")

    logger.info(f"Done. All recent reports saved to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
