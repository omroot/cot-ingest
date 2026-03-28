"""
ICE Futures Europe COT data loader.

Data file:
  downloads/ice/ice_cot.csv

ICE Europe reports the same disaggregated categories as the CFTC:
  Producer/Merchant, Swap Dealer, Managed Money, Other Reportables, Non-Reportable.

Covers contracts traded on ICE Futures Europe (London):
  Brent Crude, Gasoil, Cocoa, Robusta Coffee, White Sugar, Wheat, Dubai.
"""

import os
from functools import lru_cache

import numpy as np
import pandas as pd

_DATA_ROOT = os.path.join(
    os.path.dirname(__file__), os.pardir, os.pardir, os.pardir
)

_USE_COLS = [
    "Market_and_Exchange_Names",
    "As_of_Date_Form_MM/DD/YYYY",
    "CFTC_Contract_Market_Code",
    "CFTC_Commodity_Code",
    "Open_Interest_All",
    "Prod_Merc_Positions_Long_All",
    "Prod_Merc_Positions_Short_All",
    "Swap_Positions_Long_All",
    "Swap_Positions_Short_All",
    "Swap_Positions_Spread_All",
    "M_Money_Positions_Long_All",
    "M_Money_Positions_Short_All",
    "M_Money_Positions_Spread_All",
    "Other_Rept_Positions_Long_All",
    "Other_Rept_Positions_Short_All",
    "Other_Rept_Positions_Spread_All",
    "NonRept_Positions_Long_All",
    "NonRept_Positions_Short_All",
    "Conc_Gross_LE_4_TDR_Long_All",
    "Conc_Gross_LE_4_TDR_Short_All",
    "Conc_Gross_LE_8_TDR_Long_All",
    "Conc_Gross_LE_8_TDR_Short_All",
    "Change_in_Open_Interest_All",
    "Change_in_M_Money_Long_All",
    "Change_in_M_Money_Short_All",
    "Contract_Units",
    "FutOnly_or_Combined",
]

# Rename ICE columns to match the CFTC loader column names (lowercase)
_RENAME = {
    "Market_and_Exchange_Names": "market_and_exchange_names",
    "As_of_Date_Form_MM/DD/YYYY": "date",
    "CFTC_Contract_Market_Code": "cftc_contract_market_code",
    "CFTC_Commodity_Code": "cftc_commodity_code",
    "Open_Interest_All": "open_interest_all",
    "Prod_Merc_Positions_Long_All": "prod_merc_positions_long",
    "Prod_Merc_Positions_Short_All": "prod_merc_positions_short",
    "Swap_Positions_Long_All": "swap_positions_long_all",
    "Swap_Positions_Short_All": "swap__positions_short_all",
    "Swap_Positions_Spread_All": "swap__positions_spread_all",
    "M_Money_Positions_Long_All": "m_money_positions_long_all",
    "M_Money_Positions_Short_All": "m_money_positions_short_all",
    "M_Money_Positions_Spread_All": "m_money_positions_spread",
    "Other_Rept_Positions_Long_All": "other_rept_positions_long",
    "Other_Rept_Positions_Short_All": "other_rept_positions_short",
    "Other_Rept_Positions_Spread_All": "other_rept_positions_spread",
    "NonRept_Positions_Long_All": "nonrept_positions_long_all",
    "NonRept_Positions_Short_All": "nonrept_positions_short_all",
    "Conc_Gross_LE_4_TDR_Long_All": "conc_gross_le_4_tdr_long",
    "Conc_Gross_LE_4_TDR_Short_All": "conc_gross_le_4_tdr_short",
    "Conc_Gross_LE_8_TDR_Long_All": "conc_gross_le_8_tdr_long",
    "Conc_Gross_LE_8_TDR_Short_All": "conc_gross_le_8_tdr_short",
    "Change_in_Open_Interest_All": "change_in_open_interest_all",
    "Change_in_M_Money_Long_All": "change_in_m_money_long_all",
    "Change_in_M_Money_Short_All": "change_in_m_money_short_all",
    "Contract_Units": "contract_units",
    "FutOnly_or_Combined": "futonly_or_combined",
}

# Extract commodity name from market name for dropdown grouping
_COMMODITY_MAP = {
    "Brent Crude": "BRENT CRUDE",
    "Gasoil": "GASOIL",
    "Cocoa": "COCOA",
    "Robusta Coffee": "ROBUSTA COFFEE",
    "White Sugar": "WHITE SUGAR",
    "Wheat": "WHEAT",
    "Dubai": "DUBAI CRUDE",
    "1st Line": "DUBAI CRUDE",
}

_BENCHMARK_MARKETS = {
    "BRENT CRUDE": "ICE Brent Crude Futures",
    "GASOIL": "ICE Gasoil Futures",
}


def _extract_commodity(market_name) -> str:
    """Extract a commodity label from the ICE market name."""
    if not isinstance(market_name, str):
        return "UNKNOWN"
    for key, commodity in _COMMODITY_MAP.items():
        if key in market_name:
            return commodity
    return market_name


def _extract_contract_name(market_name) -> str:
    """Extract contract name without the exchange suffix."""
    if not isinstance(market_name, str):
        return "UNKNOWN"
    # Handle "Options- " (no space before dash) and normal " - "
    for sep in (" - ", "- "):
        if sep in market_name:
            return market_name.split(sep)[0].strip()
    return market_name


def _process(df: pd.DataFrame) -> pd.DataFrame:
    """Common processing for ICE data."""
    df = df.rename(columns=_RENAME)
    df = df.dropna(subset=["market_and_exchange_names"])
    df["date"] = pd.to_datetime(df["date"], format="mixed")

    num_cols = [
        "open_interest_all",
        "prod_merc_positions_long", "prod_merc_positions_short",
        "swap_positions_long_all", "swap__positions_short_all", "swap__positions_spread_all",
        "m_money_positions_long_all", "m_money_positions_short_all", "m_money_positions_spread",
        "other_rept_positions_long", "other_rept_positions_short", "other_rept_positions_spread",
        "nonrept_positions_long_all", "nonrept_positions_short_all",
        "conc_gross_le_4_tdr_long", "conc_gross_le_4_tdr_short",
        "conc_gross_le_8_tdr_long", "conc_gross_le_8_tdr_short",
        "change_in_open_interest_all",
        "change_in_m_money_long_all", "change_in_m_money_short_all",
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    df["release_date"] = df["date"] + pd.Timedelta(days=3)

    df["mm_net"] = df["m_money_positions_long_all"] - df["m_money_positions_short_all"]
    df["pm_net"] = df["prod_merc_positions_long"] - df["prod_merc_positions_short"]
    df["swap_net"] = df["swap_positions_long_all"] - df["swap__positions_short_all"]
    df["other_net"] = df["other_rept_positions_long"] - df["other_rept_positions_short"]
    df["nonrept_net"] = df["nonrept_positions_long_all"] - df["nonrept_positions_short_all"]

    df["commodity_name"] = df["market_and_exchange_names"].apply(_extract_commodity)
    df["contract_market_name"] = df["market_and_exchange_names"].apply(_extract_contract_name)

    for col in ("commodity_name", "contract_market_name"):
        df[col] = df[col].astype("category")

    return df.sort_values("date").reset_index(drop=True)


@lru_cache(maxsize=1)
def load_ice() -> pd.DataFrame:
    """Load ICE COT futures-only data."""
    path = os.path.join(_DATA_ROOT, "downloads", "ice", "ice_cot.csv")
    df = pd.read_csv(path, usecols=_USE_COLS, low_memory=False)
    df = df[df["FutOnly_or_Combined"] == "FutOnly"]
    return _process(df)


@lru_cache(maxsize=1)
def load_ice_combined() -> pd.DataFrame:
    """Load ICE COT combined (futures + options) data."""
    path = os.path.join(_DATA_ROOT, "downloads", "ice", "ice_cot.csv")
    df = pd.read_csv(path, usecols=_USE_COLS, low_memory=False)
    df = df[df["FutOnly_or_Combined"] == "Combined"]
    return _process(df)


def _get_df(contract_type: str = "futures_only") -> pd.DataFrame:
    if contract_type == "combined":
        return load_ice_combined()
    return load_ice()


# ── dropdown helpers ─────────────────────────────────────────────────────

def get_commodities(contract_type: str = "futures_only") -> list[dict]:
    df = _get_df(contract_type)
    names = sorted(df["commodity_name"].dropna().unique())
    return [{"label": n, "value": n} for n in names]


def get_markets(commodity_name: str, contract_type: str = "futures_only") -> list[dict]:
    df = _get_df(contract_type)
    sub = df[df["commodity_name"] == commodity_name]
    names = sorted(sub["contract_market_name"].dropna().unique())
    return [{"label": n, "value": n} for n in names]


def get_default_market(commodity_name: str, contract_type: str = "futures_only") -> str | None:
    markets = get_markets(commodity_name, contract_type)
    if not markets:
        return None
    market_labels = [m["value"] for m in markets]

    benchmark = _BENCHMARK_MARKETS.get(commodity_name)
    if benchmark and benchmark in market_labels:
        return benchmark

    df = _get_df(contract_type)
    sub = df[df["commodity_name"] == commodity_name]
    counts = sub["contract_market_name"].value_counts()
    return counts.index[0] if not counts.empty else market_labels[0]


# ── filtered data ────────────────────────────────────────────────────────

def get_ice_series(commodity_name: str, market: str, contract_type: str = "futures_only") -> pd.DataFrame:
    df = _get_df(contract_type)
    sub = df[
        (df["commodity_name"] == commodity_name) &
        (df["contract_market_name"] == market)
    ].copy()
    return sub.sort_values("date").reset_index(drop=True)


# ── analytics ────────────────────────────────────────────────────────────

def compute_zscore(series: pd.Series, lookback: int = 52) -> pd.Series:
    roll_mean = series.rolling(lookback, min_periods=max(1, lookback // 2)).mean()
    roll_std = series.rolling(lookback, min_periods=max(1, lookback // 2)).std()
    return (series - roll_mean) / roll_std.replace(0, np.nan)


def compute_kpis(sub: pd.DataFrame, lookback: int = 52, net_col: str = "mm_net") -> dict:
    if sub.empty:
        return {
            "net_val": None, "wow_change": None, "net_pct_oi": None,
            "zscore": None, "top4_conc_long": None, "top4_conc_short": None,
            "latest_date": None,
        }

    latest = sub.iloc[-1]
    prev = sub.iloc[-2] if len(sub) > 1 else None

    net_val = latest[net_col]
    wow_change = net_val - prev[net_col] if prev is not None else None
    oi = latest["open_interest_all"]
    net_pct_oi = (net_val / oi * 100) if oi and oi != 0 else None

    zs = compute_zscore(sub[net_col], lookback)
    zscore = zs.iloc[-1] if not zs.empty else None

    return {
        "net_val": net_val,
        "wow_change": wow_change,
        "net_pct_oi": net_pct_oi,
        "zscore": round(zscore, 2) if zscore is not None and not np.isnan(zscore) else None,
        "top4_conc_long": latest.get("conc_gross_le_4_tdr_long"),
        "top4_conc_short": latest.get("conc_gross_le_4_tdr_short"),
        "latest_date": latest["date"],
    }
