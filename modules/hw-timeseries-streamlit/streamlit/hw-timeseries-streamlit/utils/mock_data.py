"""
Data for HW Time Series Streamlit: uses live CDF time series (edr_training_*) when available, mock otherwise.
Run scripts/populate_edr_timeseries.py to populate CDF before using the app.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from utils.tag_lookup import get_all_flares, get_flare_config, is_tag_live, get_tag_identifier
from utils.cdf_data import fetch_timeseries_data


def generate_mock_flares() -> List[Dict]:
    return get_all_flares()


def load_flare_config() -> List[Dict]:
    return get_all_flares()


# Tag type -> dataframe column for composition
_COMP_TAG_TO_COL = {
    "nitrogen": "nitrogen_pct",
    "co2": "co2_pct",
    "methane": "methane_pct",
    "ethane": "ethane_pct",
    "other_voc": "other_voc_pct",
}


def generate_mock_flare_data(
    flare_id: str,
    start_time: datetime,
    end_time: datetime,
    sampling_rate: str = "1h"
) -> pd.DataFrame:
    flare_config = get_flare_config(flare_id)
    if not flare_config:
        raise ValueError(f"Flare {flare_id} not found in configuration")

    mock_data = flare_config.get("mock_data", {})
    flow_range = mock_data.get("flow_rate_range", [100000, 200000])
    heat_range = mock_data.get("heat_value_range", [900, 1000])
    comp = mock_data.get("composition", {})

    freq_map = {"15min": "15min", "1h": "1h", "1d": "1d"}
    freq = freq_map.get(sampling_rate, "1h")
    timestamps = pd.date_range(start=start_time, end=end_time, freq=freq)
    n_points = len(timestamps)
    data = {"timestamp": timestamps}

    # Flow rate – live or mock
    flow_rate = None
    flow_rate_source = "mock"
    if is_tag_live(flare_id, "flow_rate"):
        ts_identifier = get_tag_identifier(flare_id, "flow_rate")
        if ts_identifier:
            live_df = fetch_timeseries_data(ts_identifier, start_time, end_time, sampling_rate)
            if live_df is not None and not live_df.empty:
                flow_rate = _align_timeseries(live_df, timestamps)
                flow_rate_source = "live"
    if flow_rate is None:
        flow_rate = _generate_mock_flow_rate(timestamps, flow_range)
    data["flow_rate"] = flow_rate
    data["flow_rate_source"] = flow_rate_source

    # Heat value – live or mock
    heat_value = None
    if is_tag_live(flare_id, "heat_value"):
        ts_identifier = get_tag_identifier(flare_id, "heat_value")
        if ts_identifier:
            live_df = fetch_timeseries_data(ts_identifier, start_time, end_time, sampling_rate)
            if live_df is not None and not live_df.empty:
                heat_value = _align_timeseries(live_df, timestamps)
    if heat_value is None:
        base_heat = np.random.uniform(heat_range[0], heat_range[1], n_points)
        heat_value = base_heat + (flow_rate - np.nanmean(flow_rate)) / 10000
    data["heat_value"] = heat_value

    # Composition – live from CDF where configured, else mock
    comp_arrays = {}
    for tag_type, col in _COMP_TAG_TO_COL.items():
        arr = None
        if is_tag_live(flare_id, tag_type):
            ts_identifier = get_tag_identifier(flare_id, tag_type)
            if ts_identifier:
                live_df = fetch_timeseries_data(ts_identifier, start_time, end_time, sampling_rate)
                if live_df is not None and not live_df.empty:
                    arr = _align_timeseries(live_df, timestamps)
        if arr is None:
            # Config keys: nitrogen_range, co2_range, methane_range, ethane_range, other_voc_range
            rng_key = f"{tag_type}_range"
            rng = comp.get(rng_key, [10, 20])
            if isinstance(rng, list) and len(rng) >= 2:
                arr = np.random.uniform(rng[0], rng[1], n_points)
            else:
                arr = np.random.uniform(10, 20, n_points)
        comp_arrays[col] = arr

    # Normalize composition to 100%
    total = sum(comp_arrays.values())
    for col, arr in comp_arrays.items():
        data[col] = (arr / total) * 100 if np.any(total > 0) else arr

    # Data quality
    data["data_quality"] = np.random.choice([0, 1, 2], size=n_points, p=[0.95, 0.04, 0.01])
    df = pd.DataFrame(data)

    if flow_rate_source == "mock":
        missing_probability = np.random.uniform(0.05, 0.10)
        missing_mask = np.random.random(n_points) < missing_probability
        df.loc[missing_mask, ["flow_rate", "heat_value"]] = np.nan

    return df


def _generate_mock_flow_rate(timestamps: pd.DatetimeIndex, flow_range: List[float]) -> np.ndarray:
    n_points = len(timestamps)
    hours = np.array([t.hour for t in timestamps])
    daily_pattern = 1.0 + 0.2 * np.sin(2 * np.pi * (hours - 6) / 24)
    base_flow = np.random.uniform(flow_range[0], flow_range[1], n_points)
    flow_rate = base_flow * daily_pattern
    trend = np.linspace(0, np.random.uniform(-0.1, 0.1), n_points)
    flow_rate = flow_rate * (1 + trend)
    spike_probability = 0.02
    spikes = np.random.random(n_points) < spike_probability
    flow_rate[spikes] = flow_rate[spikes] * np.random.uniform(2.0, 3.5)
    return flow_rate


def _align_timeseries(live_df: pd.DataFrame, target_timestamps: pd.DatetimeIndex) -> np.ndarray:
    live_df = live_df.set_index("timestamp")
    target_series = pd.Series(index=target_timestamps, dtype=float)
    combined = pd.concat([live_df["value"], target_series]).sort_index()
    combined = combined[~combined.index.duplicated(keep="first")]
    combined = combined.ffill()
    result = combined.reindex(target_timestamps)
    return result.values


def add_realistic_patterns(df: pd.DataFrame) -> pd.DataFrame:
    return df
