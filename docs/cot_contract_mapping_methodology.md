# COT Contract Mapping - Methodology

How `cot_contract_mapping_summary.csv` is constructed.

## CFTC Contracts

For each future, we filter the `disaggregated_combined.csv` by `commodity_name`
to get the initial candidate set, then manually inspect `market_and_exchange_names`
to separate flat price contracts from spreads and diffs.

### Step 1 - Filter by `commodity_name`

| Future | Bloomberg Ticker | `commodity_name` keyword(s) |
|--------|------------------|-----------------------------|
| WTI Crude Oil | CL | `CRUDE OIL` |
| Brent Crude Oil | CO | `CRUDE OIL` (same bucket as WTI) |
| Heating Oil / ULSD | HO | `HEATING OIL` (matches 5 values: `HEATING OIL-DIESEL-GASOIL`, `DIESEL/HEATING OIL`, `BIODIESEL/HEATING OIL`, `JET FUEL/HEATING OIL`, `HEATING OIL/CRUDE OIL SPREADS`) |
| Gasoline (RBOB) | XB | `GASOLINE` + `UNLEADED` (matches `GASOLINE`, `UNLEADED GAS/CRUDE OIL SPREADS`) |
| Gasoil | QS | `GASOIL` within the `HEATING OIL` results above |

Note: `CRUDE OIL` is a single broad bucket containing WTI, Brent, Dubai, Oman,
WCS, and all their derivatives. WTI and Brent flat price contracts are separated
by manual inspection of `market_and_exchange_names`.

### Step 2 - Browse `market_and_exchange_names` and remove spreads/diffs

From the filtered results, we read each `market_and_exchange_names` and remove
anything that is clearly a spread, diff, crack, or calendar swap. Indicators:

- Contract name contains `SPREAD`, `SPR`, `CRACK`, `CRK`, `DIFF`, `VS`,
  `CALENDAR`, `CAL SWAP`, `UP-DOWN`, `BALMO`, `BASIS`
- Contract references two products (e.g. `RBOB/BRENT`, `WTI-BRENT`,
  `HEATING OIL/RDAM GASOIL`, `JET/GASOIL`)
- Contract references a location basis (e.g. `MARS vs WTI`, `HOUSTON/WTI`,
  `WCS CUSHING`, `SING GASOIL`, `FOB RDM`)

What remains after removing these are the flat price contracts - outright
futures, financial lookalikes, e-minis, micros, and vanilla options on the
flat price.

### Step 3 - Verify with `cftc_contract_market_code`

Each surviving contract is identified by its unique `cftc_contract_market_code`.
We record this code so the mapping is reproducible and can be applied
programmatically.

## ICE Europe Contracts

The ICE COT publication (`ice_cot.csv`) only covers contracts traded on ICE
Futures Europe. From our commodity set, only two futures come from ICE Europe:

| Future | Bloomberg Ticker | `Market_and_Exchange_Names` |
|--------|------------------|----------------------------|
| Brent Crude Oil | CO | `ICE Brent Crude Futures and Options - ICE Futures Europe` |
| Gasoil | QS | `ICE Gasoil Futures and Options - ICE Futures Europe` |

These are the primary benchmark contracts for Brent and Gasoil respectively.
No filtering or exclusion logic is needed - each is a single flat price contract.

## Output

The notebook `notebooks/generate_cot_contract_mapping.ipynb` encodes all the
above decisions as Python dicts, looks up exact contract names from the source
data files, and writes `docs/cot_contract_mapping_summary.csv`.

Each row in the CSV records:
- Which future it belongs to and the Bloomberg ticker
- The exact `cftc_contract_market_code` and `market_and_exchange_names` from the data
- Source (`CFTC` or `ICE`)
- Whether it was selected as flat price (`Yes` / `No`)
- The exclusion category and rationale if not selected

To regenerate, run the notebook end-to-end.
