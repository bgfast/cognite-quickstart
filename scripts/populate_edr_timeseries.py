#!/usr/bin/env python3
"""
Populate Cognite time series with sample data for HW Time Series Streamlit.

Creates time series and datapoints for use with the HW Time Series Streamlit app.
Pattern based on azure-eventhub-extractor: time_series.create() and time_series.data.insert().

Usage:
  cdfenv bgfast   # or set CDF env
  python scripts/populate_edr_timeseries.py

Requires: CDF credentials (CDF_PROJECT, CDF_URL, IDP_*). Loads from env or ~/envs/.env.bluefield.cog-bgfast.bgfast.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import os
import sys
import numpy as np

# Load CDF env (same pattern as streamlit-github-deployer)
def _load_cdf_env():
    env_path = os.path.expanduser("~/envs/.env.bluefield.cog-bgfast.bgfast")
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path, override=True)
        except ImportError:
            pass
_load_cdf_env()

# External ID prefix for all time series (HW Time Series Streamlit reads by this)
EXTERNAL_ID_PREFIX = "edr_training_"

# Sources and tags to create (must match streamlit tag_lookup structure; IDs kept for CDF compatibility)
FLARES = [
    {"id": "FLARE_BP1_001", "name": "Source 1", "unit": "Unit A"},
    {"id": "FLARE_BP2_001", "name": "Source 2", "unit": "Unit B"},
]

# Tag types and metadata (name, unit, description)
TAG_SPECS: Dict[str, Dict[str, str]] = {
    "flow_rate": {"name": "Flow Rate", "unit": "scf/hr", "description": "Flow rate"},
    "heat_value": {"name": "Heat Value", "unit": "BTU/scf", "description": "Heat value"},
    "nitrogen_pct": {"name": "Nitrogen %", "unit": "mol%", "description": "Nitrogen percentage"},
    "co2_pct": {"name": "CO2 %", "unit": "mol%", "description": "CO2 percentage"},
    "methane_pct": {"name": "Methane %", "unit": "mol%", "description": "Methane percentage"},
    "ethane_pct": {"name": "Ethane %", "unit": "mol%", "description": "Ethane percentage"},
    "other_voc_pct": {"name": "Other VOC %", "unit": "mol%", "description": "Other VOC percentage"},
}

# Mock ranges per source (flow_rate, heat_value, composition) for realistic data
FLARE_RANGES = {
    "FLARE_BP1_001": {
        "flow_rate": [12000, 27000],
        "heat_value": [830, 920],
        "composition": {"nitrogen": [11.96, 13.02], "co2": [0.35, 0.46], "methane": [78.16, 81.53], "ethane": [2.15, 2.35], "other_voc": [0.5, 2.0]},
    },
    "FLARE_BP2_001": {
        "flow_rate": [15000, 30000],
        "heat_value": [840, 910],
        "composition": {"nitrogen": [12.0, 13.0], "co2": [0.36, 0.45], "methane": [78.5, 81.0], "ethane": [2.20, 2.40], "other_voc": [0.6, 2.2]},
    },
}


def generate_datapoints(
    flare_id: str,
    tag_key: str,
    start: datetime,
    end: datetime,
    freq_hours: int = 1,
) -> List[Dict[str, Any]]:
    """Generate sample datapoints for one time series."""
    ranges = FLARE_RANGES.get(flare_id, FLARE_RANGES["FLARE_BP1_001"])
    datapoints = []
    current = start
    np.random.seed(hash(flare_id + tag_key) % (2**32))

    while current <= end:
        ts_ms = int(current.timestamp() * 1000)
        if tag_key == "flow_rate":
            lo, hi = ranges["flow_rate"]
            # Slight daily pattern
            hour = current.hour
            mult = 1.0 + 0.15 * np.sin(2 * np.pi * (hour - 6) / 24)
            value = float(np.clip(np.random.uniform(lo, hi) * mult, lo, hi * 1.1))
        elif tag_key == "heat_value":
            lo, hi = ranges["heat_value"]
            value = float(np.random.uniform(lo, hi))
        elif tag_key.endswith("_pct"):
            comp = tag_key.replace("_pct", "")
            comp_ranges = ranges["composition"]
            if comp in comp_ranges:
                lo, hi = comp_ranges[comp]
                value = float(np.random.uniform(lo, hi))
            else:
                value = 0.0
        else:
            value = 0.0

        datapoints.append({"timestamp": ts_ms, "value": value})
        current += timedelta(hours=freq_hours)

    return datapoints


def main():
    from cognite.client import CogniteClient
    from cognite.client.config import ClientConfig
    from cognite.client.credentials import OAuthClientCredentials
    from cognite.client.data_classes import TimeSeries

    cdf_url = os.getenv("CDF_URL")
    cdf_project = os.getenv("CDF_PROJECT")
    client_id = os.getenv("IDP_CLIENT_ID")
    client_secret = os.getenv("IDP_CLIENT_SECRET")
    token_url = os.getenv("IDP_TOKEN_URL")
    if not all([cdf_url, cdf_project, client_id, client_secret, token_url]):
        print("Missing CDF credentials. Run: cdfenv bgfast")
        print("Or set: CDF_URL, CDF_PROJECT, IDP_CLIENT_ID, IDP_CLIENT_SECRET, IDP_TOKEN_URL")
        sys.exit(1)

    credentials = OAuthClientCredentials(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        scopes=[f"{cdf_url}/.default"],
    )
    config = ClientConfig(
        client_name="edr-populate-timeseries",
        project=cdf_project,
        base_url=cdf_url,
        credentials=credentials,
    )
    client = CogniteClient(config)

    # Generate 90 days so Dashboard "Last 7/30/90 Days" and all pages have data (matches LYB mock coverage)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=90)
    freq_hours = 1

    # 1) Create time series
    to_create: List[TimeSeries] = []
    for flare in FLARES:
        flare_id = flare["id"]
        for tag_key, spec in TAG_SPECS.items():
            external_id = f"{EXTERNAL_ID_PREFIX}{flare_id}_{tag_key}"
            to_create.append(
                TimeSeries(
                    external_id=external_id,
                    name=f"{flare['name']} - {spec['name']}",
                    description=spec.get("description", ""),
                    unit=spec.get("unit"),
                )
            )

    try:
        client.time_series.create(to_create)
        print(f"Created {len(to_create)} time series (prefix: {EXTERNAL_ID_PREFIX})")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print(f"Time series already exist (ok): {len(to_create)}")
        else:
            raise

    # 2) Insert datapoints in batches (one external_id per call)
    batch_size = 10000
    for flare in FLARES:
        flare_id = flare["id"]
        for tag_key in TAG_SPECS:
            external_id = f"{EXTERNAL_ID_PREFIX}{flare_id}_{tag_key}"
            dps = generate_datapoints(flare_id, tag_key, start_time, end_time, freq_hours)
            for i in range(0, len(dps), batch_size):
                chunk = [{"timestamp": dp["timestamp"], "value": dp["value"]} for dp in dps[i : i + batch_size]]
                client.time_series.data.insert(datapoints=chunk, external_id=external_id)
            print(f"  {external_id}: {len(dps)} datapoints")

    print("Done. Run the HW Time Series Streamlit app; tag_lookup uses external_id (edr_training_*) for live data.")


if __name__ == "__main__":
    main()
