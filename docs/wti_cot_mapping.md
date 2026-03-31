# WTI Crude Oil COT Mapping: Flat Price Positioning

## Objective

Map all publicly available WTI Crude Oil COT contracts that contribute to
**flat price exposure**. We exclude spreads, diffs, cracks, and inter-commodity
contracts — those represent relative value bets, not directional WTI positioning.

## Data Sources

WTI positioning sits entirely within the CFTC's jurisdiction, but spans
multiple exchanges:

| Source | Exchange | Regulator | Report |
|--------|----------|-----------|--------|
| **CFTC** | NEW YORK MERCANTILE EXCHANGE | US CFTC | CFTC disaggregated combined |
| **CFTC** | ICE FUTURES EUROPE (CFTC-reported) | US CFTC | CFTC disaggregated combined |
| **CFTC** | ICE FUTURES ENERGY DIV | US CFTC | CFTC disaggregated combined |
| **CFTC** | DUBAI MERCANTILE EXCHANGE | US CFTC | CFTC disaggregated combined |

Note: The CFTC reports on certain ICE contracts because they are accessible to
US traders. These are **not** the same as ICE Europe's own COT publication.

## Commodity Name Filter in `disaggregated_combined.csv`

Searching for "crude" in the `commodity_name` column returns multiple values:

| `commodity_name` | Content | Flat Price WTI? |
|------------------|---------|-----------------|
| **CRUDE OIL** | WTI benchmark + all crude-related contracts (Brent, Dubai, WCS, diffs, calendar swaps) | Partially — contains WTI flat price **and** many non-WTI / non-flat-price contracts |
| DIESEL/CRUDE OIL | ULSD crack spreads | No — crack spreads |
| FUEL OIL/CRUDE OIL | Fuel oil crack spreads | No — crack spreads |
| HEATING OIL/CRUDE OIL SPREADS | HO/Gasoil crack spreads | No — crack spreads |
| NAPHTHA/CRUDE OIL | Naphtha crack spreads | No — crack spreads |
| UNLEADED GAS/CRUDE OIL SPREADS | Gasoline crack spreads | No — crack spreads |

The `CRUDE OIL` bucket is very broad — it contains WTI, Brent, Dubai, Oman,
Canadian heavy, and all their associated swaps, spreads, and diffs. Filtering
by `commodity_name` alone is **not sufficient**. You must filter by
`cftc_contract_market_code` to isolate WTI flat price contracts.

## CFTC — WTI Flat Price Contracts

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Type | Flat Price? |
|-----------------------------|----------------------------|------------------|------|-------------|
| **067651** | CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Physically-delivered futures | Yes — **the** benchmark WTI contract. This is what Bloomberg's **CL** ticker maps to. |
| **067651** | WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | (same contract, name variant) | |
| **067411** | CRUDE OIL, LIGHT SWEET - ICE FUTURES EUROPE | CRUDE OIL | Futures (WTI-referenced) | Yes — ICE-listed WTI lookalike, reported by CFTC. Aggregated into CL by Bloomberg. |
| **067411** | CRUDE OIL, LIGHT SWEET - ICE EUROPE | CRUDE OIL | (same contract, name variant) | |
| **067411** | CRUDE OIL, LIGHT SWEET-WTI - ICE FUTURES EUROPE | CRUDE OIL | (same contract, name variant) | |
| **06765I** | WTI CRUDE OIL FINANCIAL - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Cash-settled futures | Yes — WTI financial settlement |
| **067A55** | Micro WTI CRUDE OIL FINANCIAL - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Cash-settled micro futures | Yes — micro-sized WTI flat price |
| **067655** | E-MINI CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | E-mini futures | Yes — smaller-sized WTI flat price |
| **06765C** | CRUDE OIL AVG PRICE OPTIONS - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Asian-style options | Yes — options on WTI flat price |
| **06765B** | EUR STYLE CRUDE OIL OPTIONS - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | European-style options | Yes — options on WTI flat price |
| **06741Q** | WTI CRUDE OIL 1ST LINE - ICE FUTURES ENERGY DIV | CRUDE OIL | Cash-settled futures | Yes — ICE Energy Div WTI flat price |

## CFTC — Excluded Contracts

### Brent Flat Price (separate ticker — see `brent_cot_mapping.md`)

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 06765J | BRENT FINANCIAL - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent flat price, not WTI |
| 06765T | BRENT CRUDE OIL LAST DAY - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent flat price, not WTI |
| 06765T | BRENT LAST DAY - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | (same contract, name variant) |
| 06765Y | BRENT AVG PRICE OPTIONS - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent options, not WTI |
| 06765X | EUR STYLE BRENT OPTIONS - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent options, not WTI |

### Other Crude Grades (different product)

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 067DU1 | OMAN CRUDE OIL - DUBAI MERCANTILE EXCHANGE | CRUDE OIL | Oman crude — different grade and delivery |
| 067A49 | CANADIAN HVY CRUDE NET ENRGY - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Western Canadian Select — different grade |
| 067A75 | WCS OIL NET ENERGY MONTHLY IND - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WCS index — different grade |

### Inter-Commodity Spreads

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 06765L | WTI-BRENT CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WTI vs Brent spread |
| 06765L | WTI-BRENT CALENDAR - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | (same contract, name variant) |
| 06765Z | WTI-BRENT SPREAD OPTION - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WTI vs Brent spread option |
| 06765O | BRENT-DUBAI SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent vs Dubai spread |
| 06765G | DUBAI CRUDE OIL CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Dubai calendar spread |
| 06765M | DATED TO FRONTLINE BRENT SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent structure spread |
| 06765N | BRENT (ICE) CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Brent calendar spread |
| 06741R | WTI 1st Line-Brent 1st Line - ICE FUTURES ENERGY DIV | CRUDE OIL | WTI vs Brent spread |

### Location / Quality Diffs

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 06742R | ARGUS MARS vs WTI TRADE MONTH - ICE FUTURES ENERGY DIV | CRUDE OIL | Mars vs WTI quality diff |
| 06742U | ARGUS WTI Mid/WTI TRADE MONTH - ICE FUTURES ENERGY DIV | CRUDE OIL | WTI Midland vs Cushing basis |
| 06743D | ARGUS WTI HOUSTON/WTI TRADE MO - ICE FUTURES ENERGY DIV | CRUDE OIL | WTI Houston vs Cushing basis |
| 067A71 | WTI MIDLAND ARGUS VS WTI TRADE - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WTI Midland vs Cushing basis |
| 0676A5 | WTI  HOUSTON ARGUS/WTI TR MO - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WTI Houston vs Cushing basis |
| 0676A6 | WTI  HOUSTON ARGUS/WTI BALMO - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | WTI Houston vs Cushing balmo basis |
| 06739B | CRUDE DIFF-WCS CUSHING/WTI 1ST - ICE FUTURES ENERGY DIV | CRUDE OIL | WCS vs WTI diff |
| 06739C | CRUDE DIFF-WCS HOUSTON/WTI 1ST - ICE FUTURES ENERGY DIV | CRUDE OIL | WCS vs WTI Houston diff |
| 06742G | CRUDE DIFF-TMX WCS 1A INDEX - ICE FUTURES ENERGY DIV | CRUDE OIL | Canadian TMX pipeline basis |
| 06742T | CRUDE DIFF-TMX SW 1A INDEX - ICE FUTURES ENERGY DIV | CRUDE OIL | Canadian TMX pipeline basis |
| 06743A | CONDENSATE DIF-TMX C5 1A INDEX - ICE FUTURES ENERGY DIV | CRUDE OIL | Condensate vs TMX diff |

### Calendar Spread Options

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 067657 | CRUDE OIL CAL SPREAD OPTIONS - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Time spread options |
| 067A28 | CRUDE OIL CAL SPREAD OPT FIN - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Financial calendar spread options |
| 06765A | WTI CRUDE OIL CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | Calendar roll spread |
| 06765A | WTI CRUDE OIL CALENDAR - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | (same contract, name variant) |
| 06765A | WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE EXCHANGE | CRUDE OIL | (same contract, name variant) |

### Crack Spreads (product vs crude — in other `commodity_name` buckets)

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 022A09 | GULF COAST ULSD PLATT CRACK - NEW YORK MERCANTILE EXCHANGE | DIESEL/CRUDE OIL | ULSD vs crude crack |
| 022A09 | GULF COAST ULSD CRACK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | DIESEL/CRUDE OIL | (same contract, name variant) |
| 86565A | GULF # 6 FUEL OIL CRACK SWAP - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | Fuel oil vs crude crack |
| 86565A | GULF # 6 FUEL OIL CRACK - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | (same contract, name variant) |
| 86565C | 3.5% FUEL OIL RDAM CRACK SPR - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | Fuel oil vs crude crack |
| 86565D | 1% FUEL OIL NWE CRACK SPR - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | Fuel oil vs crude crack |
| 86565G | RTD 3.5% FUEL OIL CRK SPD SWP - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | Fuel oil vs crude crack |
| 86565N | GULF#6 FUELOIL BRENT CRACK SWP - NEW YORK MERCANTILE EXCHANGE | FUEL OIL/CRUDE OIL | Fuel oil vs Brent crack |
| 865392 | MARINE .5% FOB USGC/BRENT 1st - ICE FUTURES ENERGY DIV | FUEL OIL/CRUDE OIL | Marine fuel vs Brent crack |
| 86665A | NAPHTHA CRACK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | Naphtha vs crude crack |
| 86665A | NAPHTHA CRACK SPR - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | (same contract, name variant) |
| 86665A | NAPTHA CRACK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | (same contract, name variant — typo in source) |
| 86665B | JAPAN C&F NAPHTHA CRK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | Naphtha vs crude crack |
| 86665E | MINI JAPAN C&F NAPHTHA - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | Naphtha flat price (not WTI) |
| 86665E | MINI JAPAN C&F NAPHTHA SWAP FU - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | (same contract, name variant) |
| 86665G | MINI EUROPE NAPHTHA BALMO SWAP - NEW YORK MERCANTILE EXCHANGE | NAPHTHA/CRUDE OIL | Naphtha balmo (not WTI) |
| 86765C | GASOIL CRACK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL/CRUDE OIL SPREADS | Gasoil vs crude crack |
| 967652 | RBOB CRACK SPREAD SWAP - NEW YORK MERCANTILE EXCHANGE | UNLEADED GAS/CRUDE OIL SPREADS | Gasoline vs crude crack |
| 967654 | EUROBOB OXY NWE CRK SPR - NEW YORK MERCANTILE EXCHANGE | UNLEADED GAS/CRUDE OIL SPREADS | Eurobob vs crude crack |

## Current Mapping (Bloomberg CL)

Bloomberg's **CL** aggregates two contract codes per reporting date:

```
CL = 067651 (CRUDE OIL, LIGHT SWEET - NEW YORK MERCANTILE EXCHANGE)
   + 067411 (CRUDE OIL, LIGHT SWEET - ICE FUTURES EUROPE)
```

This is the only ticker in our coverage that uses **multi-exchange aggregation**.
All other tickers map to a single contract.

## Flat Price Selection Logic

Same principle as the Brent and HO mappings: a contract is included if a move in
the WTI flat price directly creates P&L for the holder. Excluded if exposure is
only to a **difference** between two prices.

The test: if WTI Cushing moves $1/bbl and everything else (Brent, Dubai, Mars,
Midland, products) moves $1 in the same direction, does the position make or
lose money? If no, it's a spread — exclude it.

Note: `06765A` (WTI CRUDE OIL CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE) is
excluded despite being "WTI" because it represents the **time spread** between
two WTI contract months, not outright flat price exposure. If both months move
$1, the P&L is zero.
