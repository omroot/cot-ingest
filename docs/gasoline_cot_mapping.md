# Gasoline (RBOB) COT Mapping: Flat Price Positioning

## Objective

Map all publicly available Gasoline / RBOB COT contracts that contribute to
**flat price exposure**. We exclude spreads, diffs, cracks, and location basis
contracts — those represent relative value bets, not directional gasoline
positioning.

## Data Sources

Like Heating Oil, Gasoline positioning sits entirely within the CFTC's
jurisdiction. There is no ICE Europe gasoline contract.

| Source | Exchange | Regulator | Report |
|--------|----------|-----------|--------|
| **CFTC** | NEW YORK MERCANTILE EXCHANGE | US CFTC | CFTC disaggregated combined |
| **CFTC** | ICE FUTURES ENERGY DIV | US CFTC | CFTC disaggregated combined |

## Commodity Name Filter in `disaggregated_combined.csv`

Searching for "gasoline" or "unleaded" in the `commodity_name` column returns
two values:

| `commodity_name` | Content | Flat Price Gasoline? |
|------------------|---------|---------------------|
| **GASOLINE** | RBOB benchmark + financial swaps, regional grades, spreads, cracks | Partially — contains flat price **and** spreads/cracks/regional diffs |
| UNLEADED GAS/CRUDE OIL SPREADS | Gasoline crack spreads | No — crack spreads only |

Note: Natural gasoline (NGL) contracts appear under `commodity_name` =
`NATURAL GAS LIQUIDS` and are an entirely different product — not included here.

## CFTC — Gasoline Flat Price Contracts

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Type | Flat Price? |
|-----------------------------|----------------------------|------------------|------|-------------|
| **111659** | GASOLINE BLENDSTOCK (RBOB) - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Physically-delivered futures | Yes — **the** benchmark RBOB contract. This is what Bloomberg's **XB** ticker maps to. |
| **111659** | GASOLINE RBOB - NEW YORK MERCANTILE EXCHANGE | GASOLINE | (same contract, name variant) | |
| **11165J** | RBOB GASOLINE FINANCIAL - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Cash-settled futures | Yes — RBOB financial settlement |
| **111416** | RBOB GASOLINE 1ST LINE - ICE FUTURES ENERGY DIV | GASOLINE | Cash-settled futures | Yes — ICE Energy Div RBOB flat price |

## CFTC — Excluded Contracts

### Calendar / Up-Down Swaps

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 11165K | RBOB CALENDAR SWAP - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Calendar roll spread |
| 11165K | RBOB CALENDAR - NEW YORK MERCANTILE EXCHANGE | GASOLINE | (same contract, name variant) |
| 11165L | RBOB UP-DOWN CAL SWAP - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Up-down calendar spread |
| 11165L | RBOB UP-DOWN CAL - NEW YORK MERCANTILE EXCHANGE | GASOLINE | (same contract, name variant) |

### Regional Grades / Location Basis

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 111A08 | GRP 3 SOC GAS VS RBOB SPR - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Group 3 sub-octane vs RBOB basis |
| 111A31 | GULF COAST UNL 87 GAS M2 PL RB - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Gulf Coast unleaded vs RBOB basis |
| 111A34 | GULF COAST CBOB GAS A2 PL RBOB - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Gulf Coast CBOB vs RBOB basis |
| 111A11 | SINGAPORE MOGUS 92 SWAP FUTURE - NEW YORK MERCANTILE EXCHANGE | GASOLINE | Singapore gasoline — different product and location |
| 111A11 | SINGAPORE MOGUS 92 - NEW YORK MERCANTILE EXCHANGE | GASOLINE | (same contract, name variant) |
| 111A47 | MINI EUROBOB GAS OXY NWE - NEW YORK MERCANTILE EXCHANGE | GASOLINE | European gasoline — different product and location |

### Crack Spreads (gasoline vs crude)

| `cftc_contract_market_code` | `market_and_exchange_names` | `commodity_name` | Reason Excluded |
|-----------------------------|----------------------------|------------------|-----------------|
| 111415 | GASOLINE CRK-RBOB/BRENT 1st - ICE FUTURES ENERGY DIV | GASOLINE | RBOB vs Brent crack |
| 111A41 | RBOB GASOLINE/BRENT CRACK SPRD - NEW YORK MERCANTILE EXCHANGE | GASOLINE | RBOB vs Brent crack |
| 967652 | RBOB CRACK SPREAD SWAP - NEW YORK MERCANTILE EXCHANGE | UNLEADED GAS/CRUDE OIL SPREADS | RBOB vs WTI crack |
| 967654 | EUROBOB OXY NWE CRK SPR - NEW YORK MERCANTILE EXCHANGE | UNLEADED GAS/CRUDE OIL SPREADS | Eurobob vs crude crack |

## Current Mapping (Bloomberg XB)

**Bloomberg XB:** Uses only contract `111659` (GASOLINE BLENDSTOCK (RBOB) -
NEW YORK MERCANTILE EXCHANGE) from the CFTC disaggregated combined report.
This is the single dominant flat price contract for gasoline — like Heating Oil,
there is no cross-exchange aggregation needed.

## Flat Price Selection Logic

Same principle as the other commodity mappings: a contract is included if a move
in the RBOB flat price directly creates P&L for the holder. Excluded if exposure
is only to the **difference** between two prices.

The test: if RBOB moves $1/gal and everything else (crude, Brent, regional
gasoline grades, Eurobob) moves $1 in the same direction, does the position
make or lose money? If no, it's a spread — exclude it.
