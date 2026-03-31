# Brent COT Mapping: Flat Price Positioning

## Objective

Map all publicly available Brent Crude Oil COT contracts that contribute to
**flat price exposure**. We exclude spreads, diffs, and crack contracts — those
represent relative value bets, not directional Brent positioning.

## Data Sources

Brent COT positioning is split across two independent regulatory regimes:

| Source | Exchange | Regulator | Report |
|--------|----------|-----------|--------|
| **ICE Futures Europe** | ICE Europe (London) | UK FCA | ICE COT publication |
| **CFTC** | NYMEX (New York) | US CFTC | CFTC disaggregated combined |

These do **not** overlap — a position on NYMEX and a position on ICE Europe are
reported separately with no double-counting.

## ICE Europe — Primary Brent Contract

| Contract | Source File | Notes |
|----------|------------|-------|
| ICE Brent Crude Futures and Options | `downloads/ice/ice_cot.csv` | Physically-deliverable benchmark. Largest Brent OI globally. This is what Bloomberg's **CO** ticker maps to. |

This is the dominant flat price contract for Brent.

## CFTC (NYMEX) — Flat Price Brent Contracts

Extracted from `downloads/cftc/disaggregated_combined.csv`:

| Code | Contract | Type | Flat Price? |
|------|----------|------|-------------|
| **06765J** | BRENT FINANCIAL - NYMEX | Cash-settled futures | Yes — main NYMEX Brent lookalike |
| **06765T** | BRENT CRUDE OIL LAST DAY - NYMEX | Physically-delivered futures | Yes — last trading day settlement |
| **06765Y** | BRENT AVG PRICE OPTIONS - NYMEX | Asian-style options | Yes — options on Brent flat price |
| **06765X** | EUR STYLE BRENT OPTIONS - NYMEX | European-style options | Yes — options on Brent flat price |

## CFTC (NYMEX) — Excluded Contracts

These reference Brent but represent spreads, diffs, or relative value — they do
not contribute to directional flat price exposure:

| Code | Contract | Reason Excluded |
|------|----------|-----------------|
| 06765N | BRENT (ICE) CALENDAR SWAP | Time spread (front vs back months) |
| 06765L | WTI-BRENT CALENDAR SWAP | Inter-commodity spread |
| 06765Z | WTI-BRENT SPREAD OPTION | Inter-commodity spread option |
| 06765O | BRENT-DUBAI SWAP | Location spread |
| 06765M | DATED TO FRONTLINE BRENT SWAP | Structure spread (dated vs futures) |
| 111415 | GASOLINE CRK-RBOB/BRENT 1st | Crack spread |
| 111A41 | RBOB GASOLINE/BRENT CRACK SPRD | Crack spread |
| 86565N | GULF#6 FUELOIL BRENT CRACK SWP | Crack spread |
| 865392 | MARINE .5% FOB USGC/BRENT 1st | Crack spread |
| 02141R | USGC HSFO-PLATTS/BRENT 1ST LN | Crack spread |

## Current vs Potential Mapping

**Current (Bloomberg CO):** Uses only the ICE Europe Brent contract. This is
what our dashboard maps today and what Bloomberg's `cot_db.csv` reports.

**Potential (Total Brent Flat Price):** Sum ICE Europe + NYMEX flat price
contracts (06765J, 06765T, 06765Y, 06765X) to get a more complete view of
total Brent directional positioning across exchanges. This would mirror the
CL (WTI) approach, which already aggregates NYMEX + CFTC-reported ICE.

## Flat Price Selection Logic

A contract is included if a move in the Brent flat price directly creates P&L
for the holder. A contract is excluded if it only has exposure to the
**difference** between two prices (time spreads, location spreads, crack
spreads, inter-commodity spreads). The test: if Brent moves $1 and everything
else moves $1 in the same direction, does the position make or lose money? If
no, it's a spread — exclude it.
