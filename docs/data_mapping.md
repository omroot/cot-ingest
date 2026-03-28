# COT Data Mapping: Public Sources to Bloomberg Format

## Data Sources

We load Commitments of Traders (COT) data from two public sources:

1. **CFTC API** — `downloads/cftc/` — US-regulated futures (NYMEX + CFTC-reported ICE contracts)
2. **ICE Futures Europe website** — `downloads/ice/` — London-traded futures (Brent, Gasoil, etc.)

## Commodity Coverage

| Ticker | Commodity | Source | Contract Code / Market | Exchange |
|--------|-----------|--------|----------------------|----------|
| **CL** | WTI Crude Oil | CFTC | `067651` CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE | NYMEX |
| | | CFTC | `067411` CRUDE OIL, LIGHT SWEET - ICE FUTURES EUROPE | ICE (CFTC-reported) |
| **CO** | Brent Crude Oil | ICE EU | ICE Brent Crude Futures and Options - ICE Futures Europe | ICE Europe |
| **HO** | Heating Oil (ULSD) | CFTC | `022651` #2 HEATING OIL, NY HARBOR-ULSD - NEW YORK MERCANTILE EXCHANGE | NYMEX |
| **XB** | Gasoline (RBOB) | CFTC | `111659` GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE | NYMEX |
| **QS** | Gasoil | ICE EU | ICE Gasoil Futures and Options - ICE Futures Europe | ICE Europe |

Contract names are taken verbatim from the `market_and_exchange_names` column in the source CSVs.

## Bloomberg Hybrid Mapping

Marouen's `cot_db.csv` (sourced from Bloomberg) uses a **hybrid** mapping that
mixes two different CFTC classification schemes:

### Commercial = Disaggregated Producer/Merchant

Always from `disaggregated_combined.csv` (futures + options):

```
CommercialLong  = prod_merc_positions_long
CommercialShort = prod_merc_positions_short
```

This is the **narrower** definition — only physical hedgers. It excludes Swap
Dealers, who are lumped into "Commercial" in the legacy report.

### ManagedMoney — depends on data availability

**CFTC tickers (CL, HO, XB):** Legacy Non-Commercial from `legacy_combined.csv`

```
ManagedMoney_Long  = noncomm_positions_long_all
ManagedMoney_Short = noncomm_positions_short_all
```

This is the **broader** definition — includes Managed Money + Other Reportables +
their spreading positions. Bloomberg labels it "ManagedMoney" but it is actually
the legacy Non-Commercial category.

**ICE Europe tickers (CO, QS):** Disaggregated MM + Other from `ice_cot.csv`

```
ManagedMoney_Long  = M_Money_Positions_Long_All + Other_Rept_Positions_Long_All
ManagedMoney_Short = M_Money_Positions_Short_All + Other_Rept_Positions_Short_All
```

ICE Europe does not publish a legacy-format report, so there is no "Non-Commercial"
category. Bloomberg approximates it by summing Managed Money + Other Reportables
(excluding Swap Dealers).

### Why hybrid?

The disaggregated report (2009+) splits traders into 4 categories:
Producer/Merchant, Swap Dealers, Managed Money, Other Reportables.

The legacy report splits traders into 2 categories:
Commercial (= PM + Swap), Non-Commercial (= MM + Other + spreads).

Bloomberg cherry-picks:
- **Prod/Merch** from disaggregated for "Commercial" (excludes Swap Dealers)
- **Non-Commercial** from legacy for "ManagedMoney" (includes all large speculators)

The two sides are **not complementary** — they come from different classification
schemes and do not sum to total open interest.

## Multi-Exchange Aggregation

CL (WTI) sums positions across **two** contract codes per reporting date:
NYMEX WTI (`067651`) + CFTC-reported ICE Brent (`067411`). This gives a combined
crude oil view. All other tickers use a single contract.

## Report Type

All mappings use the **Combined** report (futures + delta-adjusted options),
not Futures Only.

## ICE Europe FutOnly Fallback

ICE Europe only started publishing Combined (futures + options) data around
March 2013. For CO and QS dates before 2013, the notebooks fall back to FutOnly
data. This introduces small diffs (~1-5% MAPE) because FutOnly excludes the
options delta adjustment that Bloomberg's source includes. From 2013 onward the
match is exact.

## Verification

Each commodity has a notebook under `notebooks/` that loads the raw public data,
applies the exact filters above, and compares against Marouen's `cot_db.csv`:

| Notebook | Ticker | Commercial MAPE | ManagedMoney MAPE | Notes |
|----------|--------|-----------------|-------------------|-------|
| `wti_mapping.ipynb` | CL | 0.0000% | 0.0001% | Max diff 2 contracts (multi-exchange rounding) |
| `brent_mapping.ipynb` | CO | 0.0000% | 0.0000% | Perfect from 2013+; ~3-5% pre-2013 fallback |
| `heating_oil_mapping.ipynb` | HO | 0.0000% | 0.0004% | Max diff 1 contract |
| `gasoline_mapping.ipynb` | XB | 0.0000% | 0.0002% | Max diff 1 contract |
| `gasoil_mapping.ipynb` | QS | 0.0000% | 0.0000% | Perfect from 2013+; ~1-5% pre-2013 fallback |

## CFTC Files Used

| File | Report Type | Content |
|------|-------------|---------|
| `disaggregated_combined.csv` | Disaggregated, Combined | 4 trader categories, futures + options. Used for **Commercial** (Prod/Merch). |
| `legacy_combined.csv` | Legacy/Aggregated, Combined | 2 trader categories, futures + options. Used for **ManagedMoney** (Non-Commercial). |
| `ice_cot.csv` | ICE Europe Disaggregated | 4 trader categories, FutOnly + Combined. Used for **CO** and **QS** (both sides). |
