# COT Ingest

Download, process, and visualize Commitments of Traders (COT) reports from the CFTC public API and ICE Futures Europe.

## Project Structure

```
cot-ingest/
├── src/                          # Core library
│   ├── cftc_config.py            # Credential loader (.env parser)
│   ├── cftc_downloader.py        # CFTC API client & dataset downloader
│   └── ice_downloader.py         # ICE Futures Europe COT downloader
├── dashboard/                    # Dash web application
│   ├── app.py                    # Entry point (Gunicorn-compatible)
│   ├── assets/                   # Static files (CSS)
│   └── dashboard/                # App package
│       ├── index.py              # Dash app initialization
│       ├── content.py            # Layout, routing & navbar
│       ├── config.py             # App configuration
│       ├── data/                 # Data loaders (CFTC, ICE, TFF)
│       └── layout/               # Pages & callbacks
│           ├── page_home.py              # Home — positioning snapshot
│           ├── page_cftc_positioning.py  # CFTC disaggregated positioning
│           ├── page_tff.py               # Traders in Financial Futures
│           ├── page_data_guide.py        # Documentation & reference
│           └── callbacks/                # Interactive callback handlers
├── notebooks/                    # Jupyter notebooks — data mapping verification
│   ├── wti_mapping.ipynb         # WTI Crude Oil (CL)
│   ├── brent_mapping.ipynb       # Brent Crude (CO)
│   ├── heating_oil_mapping.ipynb # Heating Oil / ULSD (HO)
│   ├── gasoline_mapping.ipynb    # RBOB Gasoline (XB)
│   └── gasoil_mapping.ipynb      # Gasoil (QS)
├── docs/                         # Documentation
│   └── data_mapping.md           # Bloomberg hybrid mapping methodology
├── downloads/                    # Downloaded data (gitignored)
│   ├── cftc/                     # CFTC CSV datasets
│   └── ice/                      # ICE Futures Europe CSV data
├── cot_data/                     # External COT reference data (gitignored)
├── cache/output/                 # Processed output CSVs (gitignored)
├── .env                          # API credentials (gitignored)
├── .env_template                 # Credential template
└── requirements.txt
```

## Setup

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API credentials**

   ```bash
   cp .env_template .env
   ```

   Edit `.env` with your CFTC API key:

   ```
   CFTC_API_KEY_ID=your_api_key_id_here
   CFTC_API_KEY_SECRET=your_api_key_secret_here
   ```

## Usage

### Download CFTC data

Download full history for a specific report type:

```bash
python -m src.cftc_downloader --dataset disaggregated
```

Download incremental updates since a date:

```bash
python -m src.cftc_downloader --dataset disaggregated --since 2025-01-01
```

Available datasets: `disaggregated`, `disaggregated_combined`, `legacy`, `legacy_combined`, `tff`, `tff_combined`.

### Download ICE data

Download full ICE Futures Europe COT history (2011–present):

```bash
python -m src.ice_downloader
```

Download from a specific year onward:

```bash
python -m src.ice_downloader --since-year 2024
```

Covers: Brent Crude, Gasoil, Cocoa, Robusta Coffee, White Sugar, Wheat, Dubai.

### Dashboard

Launch the Dash web app (default port 8070):

```bash
python dashboard/app.py
```

Production deployment with Gunicorn:

```bash
gunicorn dashboard.app:server -b 0.0.0.0:8070
```

Pages: Home (positioning snapshot), CFTC Positioning, TFF, Data Guide.

## Data Sources

- [CFTC Public Reporting API](https://publicreporting.cftc.gov) — US futures COT data
- [ICE Futures Europe](https://www.ice.com) — London-traded futures COT data
