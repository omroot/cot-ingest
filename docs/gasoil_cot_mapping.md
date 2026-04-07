# Gasoil COT Mapping: Flat Price Positioning

## Objective

Map all publicly available Gasoil COT contracts that contribute to
**flat price exposure**. We exclude spreads, diffs, cracks, and location basis
contracts — those represent relative value bets, not directional Gasoil
positioning.

## Data Sources

Gasoil positioning comes from two independent sources:

| Source | Exchange | Regulator | Report |
|--------|----------|-----------|--------|
| **ICE Futures Europe** | ICE Futures Europe (London) | UK FCA | ICE COT publication |
| **CFTC** | NEW YORK MERCANTILE EXCHANGE | US CFTC | CFTC disaggregated combined |

These do **not** overlap — a position on NYMEX and a position on ICE Europe are
reported separately with no double-counting.

Note: Gasoil is European low-sulphur gasoil (10 ppm), distinct from US
NY Harbor ULSD (Heating Oil / HO). They are related middle distillate products
but **not** fungible — different specs, delivery locations, and price levels.

## ICE Europe — Primary Gasoil Contract

| `Market_and_Exchange_Names` | `CFTC_Contract_Market_Code` | `CFTC_Market_Code` | `CFTC_Commodity_Code` | Type | Flat Price? |
|-----------------------------|-----------------------------|--------------------|----------------------|------|-------------|
| **ICE Gasoil Futures and Options - ICE Futures Europe** | (empty) | ICEU | G | Combined futures + options | Yes — **the** benchmark Gasoil contract. This is what Bloomberg's **QS** ticker maps to. |
| **ICE Gasoil Futures - ICE Futures Europe** | (empty) | ICEU | G | Futures only | Yes — same contract, FutOnly report variant. Used as fallback pre-2013. |

This is the dominant flat price contract for Gasoil globally.

## Commodity Name Filter in `disaggregated_combined.csv`

Gasoil-related CFTC contracts appear under multiple `commodity_name` values:

| `commodity_name` | Content | Flat Price Gasoil? |
|------------------|---------|-------------------|
| **HEATING OIL-DIESEL-GASOIL** | Gasoil swaps, ICE Gasoil reference contracts, options | Partially — contains gasoil flat price swaps **and** location/quality spreads |
| JET FUEL/HEATING OIL | Jet vs gasoil spreads | No — spreads only |
| HEATING OIL/CRUDE OIL SPREADS | Gasoil crack spreads | No — crack spreads |
| BIODIESEL/HEATING OIL | Biodiesel vs gasoil spreads | No — spreads only |

## CFTC (NYMEX) — Gasoil Flat Price Contracts

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Type | Flat Price? |
|-----------------------------|----------------------------|------------------|------|-------------|
| **02265V** | GASOIL (ICE) SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Cash-settled swap | Yes — NYMEX-listed swap referencing ICE Gasoil flat price |
| **022A46** | GASOIL AVG PRICE OPTIONS - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Asian-style options | Yes — options on Gasoil flat price |
| **022A24** | GASOIL (ICE) MINI CAL SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Swap | Yes — added per Marouen's review |
| **02265J** | SING GASOIL SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Swap | Yes — Singapore gasoil, added per Marouen's review |
| **022A22** | SING GASOIL BALMO SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Swap | Yes — Singapore gasoil balmo, added per Marouen's review |

## CFTC (NYMEX) — Excluded Contracts

### Location Spreads

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 022A26 | GASOIL 0.1 BARGE FOB RDM V ICE - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Rotterdam barge vs ICE Gasoil location/quality spread |
| 02265U | NYMEX HEATING OIL/RDAM GASOIL - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | HO vs Rotterdam Gasoil arb |
| 02265T | SING GASOIL ICE GASOIL SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | Singapore vs ICE Gasoil location spread |
| 02265T | SING GASOIL/RDAM GASOIL SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL-DIESEL-GASOIL | (same contract, name variant) |

### Crack Spreads (gasoil vs crude)

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 86765C | GASOIL CRACK SPR SWAP - NEW YORK MERCANTILE EXCHANGE | HEATING OIL/CRUDE OIL SPREADS | Gasoil vs crude spread |

### Jet / Biodiesel Spreads

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 86465C | SING JET KERO GASOIL SPR SWAP - NEW YORK MERCANTILE EXCHANGE | JET FUEL/HEATING OIL | Jet kerosene vs Gasoil spread |
| 86465C | SING JET KERO GASOIL SPR - NEW YORK MERCANTILE EXCHANGE | JET FUEL/HEATING OIL | (same contract, name variant) |
| 86465D | JET CIF NWE/GASOIL FUT - NEW YORK MERCANTILE EXCHANGE | JET FUEL/HEATING OIL | Jet fuel vs Gasoil spread |
| 869652 | FAM BIODIESEL V GASOIL SPR SWP - NEW YORK MERCANTILE EXCHANGE | BIODIESEL/HEATING OIL | Biodiesel vs Gasoil spread |
| 869654 | FAME BIODIESEL V GASOIL SPR SP - NEW YORK MERCANTILE EXCHANGE | BIODIESEL/HEATING OIL | Biodiesel vs Gasoil spread |

## Current Mapping (Bloomberg QS)

**Bloomberg QS:** Uses only the ICE Europe Gasoil contract from `downloads/ice/ice_cot.csv`.
This is the single dominant flat price contract for Gasoil — similar to Brent (CO),
it sits outside CFTC jurisdiction.

## Current vs Potential Mapping

**Current (Bloomberg QS):** Uses only the ICE Europe Gasoil contract.

**Potential (Total Gasoil Flat Price):** Sum ICE Europe + NYMEX flat price
contracts (`02265V`, `022A46`) to get a more complete view of total Gasoil
directional positioning across exchanges.

## Flat Price Selection Logic

Same principle as the other commodity mappings: a contract is included if a move
in the ICE Gasoil flat price directly creates P&L for the holder. Excluded if
exposure is only to the **difference** between two prices.

The test: if ICE Gasoil moves $1/tonne and everything else (crude, HO, Singapore
gasoil, jet, Rotterdam barge) moves $1 in the same direction, does the position
make or lose money? If no, it's a spread — exclude it.
