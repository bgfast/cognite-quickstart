# Cognite Quickstart Project

This project is a Hello World–style quickstart for Cognite Data Fusion (CDF), with modules for Functions, NEAT data modeling, and Streamlit apps.

## Overview

On **main**, the primary setup is the **Hello World demo set**, which includes:

- **hw-function** — Cognite Function + Streamlit integration (call a function from a Streamlit app)
- **hw-neat** — Excel-based data modeling with NEAT and a Streamlit app for CRUD
- **hw-timeseries-streamlit** — Streamlit app that reads CDF time series (e.g. `edr_training_*`)

Additional modules used by these or other configs:

- **hw-transformations** — Transformations (e.g. cleanup); deploy with its own env
- **common/foundation** — Base CDF setup and access
- **common/valhall_dm** — Data model used by some configs

## Setup Instructions

### 1. Environment Configuration

1. **Use your existing environment file from `~/envs`**:
   ```bash
   source ~/envs/your-env-file.sh
   ```

2. **Or copy the template and customize**:
   ```bash
   cp cdfenv.sh cdfenv.local.sh
   # Edit cdfenv.local.sh with your CDF project details
   source cdfenv.local.sh
   ```

   Required environment variables (see `config.all-hw.yaml` for the full list):

   - `CDF_PROJECT`, `CDF_CLUSTER`
   - `IDP_CLIENT_ID`, `IDP_CLIENT_SECRET`, `IDP_*`
   - `FUNCTION_CLIENT_ID`, `FUNCTION_CLIENT_SECRET`
   - `TRANSFORMATION_CLIENT_ID`, `TRANSFORMATION_CLIENT_SECRET`
   - `SUPERUSER_SOURCEID_ENV`, `USER_IDENTIFIER`

### 2. Deploy the Hello World Set

Use the **`all-hw`** environment (uses `config.all-hw.yaml`). Always use the **`--env`** flag, not `--config`:

```bash
cdf build --env=all-hw
cdf deploy --env=all-hw --dry-run   # optional: preview
cdf deploy --env=all-hw
```

### 3. Verify Deployment

After deployment, check in the CDF UI:

- **Functions** — Your function space (e.g. `hw-function`) and the Hello World function
- **Streamlit apps** — Hello World Function app, NEAT app, and Time Series Streamlit app
- **Data model (NEAT)** — Space and containers/views from `hw-neat` (e.g. `HWNeatBasic`)

For time series–based demos (e.g. `hw-timeseries-streamlit`), ensure time series exist. You can populate training time series with:

```bash
python scripts/populate_edr_timeseries.py
```

(Requires a suitable environment and CDF credentials.)

## Project Structure

```
cognite-quickstart/
├── config.all-hw.yaml              # Main Hello World config (hw-function, hw-neat, hw-timeseries-streamlit)
├── config.hw-function.yaml         # hw-function only
├── config.hw-neat.yaml             # hw-neat only
├── config.hw-transformations.yaml  # hw-transformations only
├── config.neat-basic.yaml          # NEAT basic demo
├── config.weather.yaml             # Weather/Valhall demo (see README.weather.md)
├── cdfenv.sh                       # Environment template
├── README.md                       # This file
├── readme.hw-all.md                # Hello World set (all-hw) details
├── readme.hw-function.md          # hw-function details
├── readme.hw-neat.md               # hw-neat details
├── readme.hw-transformations.md    # hw-transformations details
├── readme.neat-basic.md            # NEAT basic demo
├── README.weather.md               # Weather/Valhall setup
├── scripts/                        # Utility scripts
│   ├── check_syntax.py
│   ├── quick_check_mini_zips.py
│   ├── populate_edr_timeseries.py  # Populate edr_training_* time series
│   ├── test_dm_file_download.py
│   ├── list_app_packages_instances.py
│   └── delete_all_app_packages_instances.py
└── modules/
    ├── hw-function/                # Hello World function + Streamlit
    ├── hw-neat/                    # Hello World NEAT data model + Streamlit
    ├── hw-timeseries-streamlit/    # Streamlit app for time series
    ├── hw-transformations/         # Transformations (separate env)
    └── common/
        ├── foundation/
        └── valhall_dm/
```

## Other Configurations

- **Single modules**: `cdf build --env=hw-function`, `cdf build --env=hw-neat`, etc., then `cdf deploy --env=...`
- **Transformations**: `cdf build --env=hw-transformations` and `cdf deploy --env=hw-transformations`
- **NEAT basic**: `cdf build --env=neat-basic` and `cdf deploy --env=neat-basic`
- **Weather / Valhall**: See `README.weather.md` and `config.weather.yaml`

## Documentation

- **Hello World set**: `readme.hw-all.md`
- **hw-function**: `readme.hw-function.md`
- **hw-neat**: `readme.hw-neat.md`
- **hw-transformations**: `readme.hw-transformations.md`
- **NEAT basic**: `readme.neat-basic.md`
- **Weather/Valhall**: `README.weather.md`

## Troubleshooting

- **Build/deploy**: Use `--env=all-hw` (or the env name that matches your `config.<env>.yaml`). Do not use `--config` with a file path for standard deploy.
- **Functions**: Check the Functions UI for the correct space and that the function is deployed and callable.
- **Streamlit**: Open the app from the CDF UI; ensure you have the right permissions and that any required data (e.g. time series) exists.
- **NEAT**: Ensure the NEAT space and containers are deployed and that the Streamlit app’s dataset and permissions are correct.
- **Time series**: For `hw-timeseries-streamlit`, run `scripts/populate_edr_timeseries.py` if the expected time series are missing.
