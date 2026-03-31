# Heating Oil / ULSD COT Mapping: Flat Price Positioning

## Objective

Map all publicly available Heating Oil / ULSD COT contracts that contribute to
**flat price exposure**. We exclude spreads, diffs, cracks, and location basis
contracts — those represent relative value bets, not directional HO positioning.

## Data Sources

Unlike Brent, Heating Oil positioning sits entirely within the CFTC's
jurisdiction. There is no separate ICE Europe heating oil contract.

| Source | Exchange | Regulator | Report |
|--------|----------|-----------|--------|
| **CFTC** | NYMEX (New York) | US CFTC | CFTC disaggregated combined |

Note: ICE Futures Europe publishes Gasoil (QS) which is a related but distinct
product — European low-sulphur gasoil vs US ultra-low-sulphur diesel. They are
**not** fungible and trade at different price levels.

## Commodity Name Filter in `disaggregated_combined.csv`

Searching for "heating oil" in the `commodity_name` column returns **five**
distinct values — not all of which are flat price HO:

| `commodity_name` | Content | Flat Price HO? |
|------------------|---------|----------------|
| **HEATING OIL-DIESEL-GASOIL** | Benchmark HO, ULSD swaps, gasoil swaps, options | Partially — contains flat price contracts **and** gasoil/location swaps |
| DIESEL/HEATING OIL | ULSD basis and quality spread contracts | No — spreads only |
| BIODIESEL/HEATING OIL | Biodiesel vs gasoil spreads | No — spreads only |
| JET FUEL/HEATING OIL | Jet fuel vs HO/gasoil spreads | No — spreads only |
| HEATING OIL/CRUDE OIL SPREADS | Crack spreads (distillate vs crude) | No — spreads only |

Filtering on `commodity_name = HEATING OIL-DIESEL-GASOIL` alone is **not
sufficient** for flat price — that bucket still includes gasoil swaps (Singapore,
Rotterdam, ICE), location basis contracts, and calendar rolls. You must further
filter by `cftc_contract_market_code` to isolate flat price contracts.

## CFTC (NYMEX) — Flat Price Contracts

| Code | Contract | Type | Flat Price? |
|------|----------|------|-------------|
| **022651** | NY HARBOR ULSD - NYMEX | Physically-delivered futures | Yes — the benchmark HO contract. This is what Bloomberg's **HO** ticker maps to. |
| **022653** | HEATING OIL AVG PRICE OPTIONS - NYMEX | Asian-style options | Yes — options on HO flat price |
| **022654** | EUR STYLE HEATING OIL OPTIONS - NYMEX | European-style options | Yes — options on HO flat price |
| **022A05** | GULF COAST ULSD SWAP - NYMEX | Cash-settled futures | Yes — outright ULSD flat price for USGC delivery |

## CFTC (NYMEX) — Excluded Contracts

### Gasoil / Regional Swaps (different product or location basis)

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 02265V | GASOIL (ICE) SWAP | ICE Gasoil reference price — different product (European gasoil) |
| 022A24 | GASOIL (ICE) MINI CAL SWAP | Same — mini version of ICE Gasoil swap |
| 022A46 | GASOIL AVG PRICE OPTIONS | Options on gasoil, not HO |
| 02265J | SING GASOIL SWAP | Singapore gasoil — different product and location |
| 022A22 | SING GASOIL BALMO SWAP | Singapore gasoil balance-of-month |

### Crack Spreads (product vs crude)

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 86765C | GASOIL CRACK SPR SWAP | Gasoil vs crude spread |
| 022A09 | GULF COAST ULSD PLATT CRACK | USGC ULSD vs crude crack |

### Location / Quality Spreads

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 022A26 | GASOIL 0.1 BARGE FOB RDM V ICE | Rotterdam barge vs ICE Gasoil |
| 02265U | NYMEX HEATING OIL/RDAM GASOIL | HO vs Rotterdam Gasoil arb |
| 02265T | SING GASOIL ICE GASOIL SWAP | Singapore vs ICE Gasoil location spread |
| 022A60 | GRP 3 ULSD VS HEATING OIL SPR | Group 3 ULSD vs NY Harbor basis |
| 022A66 | NY ULSD VS HEATING OIL SPR SWP | ULSD vs legacy heating oil spec diff |
| 86465D | JET CIF NWE/GASOIL FUT | Jet fuel vs Gasoil spread |
| 86465A | GULF JET NY HEAT OIL SPR SWAP | Jet vs HO spread |
| 86465C | SING JET KERO GASOIL SPR SWAP | Jet kerosene vs Gasoil spread |
| 86465K | JET UP-DOWN BALMO | Jet calendar balmo |

### Up-Down / Calendar Swaps

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 022A18 | ULSD UP DOWN SWAP | Calendar roll spread |
| 022A62 | ULSD UP-DOWN BALMO SWAP | Balance-of-month calendar spread |
| 022A13 | UP DOWN GC ULSD VS HO SPR SWAP | Gulf Coast vs NY calendar + location spread |

### Biodiesel Spreads

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 869652 | FAM BIODIESEL V GASOIL SPR SWP | Biodiesel vs Gasoil spread |
| 869654 | FAME BIODIESEL V GASOIL SPR SP | Biodiesel vs Gasoil spread |

## Current Mapping

**Bloomberg HO:** Uses only contract `022651` (NY Harbor ULSD) from the CFTC
disaggregated combined report. This is the single dominant flat price contract
for heating oil — unlike Brent, there is no cross-exchange aggregation needed.

## Flat Price Selection Logic

Same principle as the Brent mapping: a contract is included if a move in the HO
flat price directly creates P&L for the holder. If the position only has exposure
to the **difference** between two prices (crack spreads, location basis, calendar
rolls, product quality diffs), it is excluded.

The test: if NY Harbor ULSD moves $1/gal and everything else (crude, gasoil,
jet, regional ULSD) moves $1 in the same direction, does the position make or
lose money? If no, it's a spread — exclude it.
