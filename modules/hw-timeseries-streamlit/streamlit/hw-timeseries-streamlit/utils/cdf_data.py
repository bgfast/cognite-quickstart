"""
CDF Data: fetch time series from Cognite Data Fusion.
Supports retrieval by external_id (e.g. edr_training_*) or by name/id.
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from utils.tag_lookup import get_live_tags, get_flare_config

try:
    from cognite.client import CogniteClient
    CDF_AVAILABLE = True
except ImportError:
    CDF_AVAILABLE = False

_client = None


def get_cdf_client() -> Optional["CogniteClient"]:
    global _client
    if not CDF_AVAILABLE:
        return None
    if _client is not None:
        return _client
    try:
        _client = CogniteClient()
        return _client
    except Exception as e:
        import streamlit as st
        st.warning(f"Failed to initialize CDF client: {e}")
        return None


def _resolve_ts_id(client: "CogniteClient", ts_name_or_id) -> Optional[int]:
    """Resolve time series name, external_id, or numeric id to internal id."""
    if isinstance(ts_name_or_id, int):
        return ts_name_or_id
    if isinstance(ts_name_or_id, str) and ts_name_or_id.isdigit():
        return int(ts_name_or_id)
    if isinstance(ts_name_or_id, str):
        # Try by external_id first (e.g. edr_training_..._flow_rate)
        try:
            ts = client.time_series.retrieve(external_id=ts_name_or_id)
            if ts:
                return ts.id
        except Exception:
            pass
        # Fallback: search by name
        for ts in client.time_series.list(limit=1000):
            if ts.name == ts_name_or_id:
                return ts.id
    return None


def find_timeseries_by_name(name: str) -> Optional[int]:
    client = get_cdf_client()
    if client is None:
        return None
    return _resolve_ts_id(client, name)


def fetch_timeseries_data(
    ts_name_or_id,
    start_time: datetime,
    end_time: datetime,
    granularity: str = "1h"
) -> Optional[pd.DataFrame]:
    """Fetch time series data from CDF (by external_id, name, or id)."""
    client = get_cdf_client()
    if client is None:
        return None
    try:
        ts_id = _resolve_ts_id(client, ts_name_or_id)
        if ts_id is None:
            import streamlit as st
            st.warning(f"Time series '{ts_name_or_id}' not found")
            return None
        datapoints = client.time_series.data.retrieve(
            id=ts_id,
            start=start_time,
            end=end_time,
            granularity=granularity,
            aggregates=["average"]
        )
        df = datapoints.to_pandas()
        if df.empty:
            return None
        df.columns = ['value']
        df = df.reset_index()
        df.columns = ['timestamp', 'value']
        return df
    except Exception as e:
        import streamlit as st
        st.warning(f"Failed to fetch data for {ts_name_or_id}: {e}")
        return None


def fetch_raw_timeseries_data(
    ts_name_or_id,
    start_time: datetime,
    end_time: datetime,
    limit: int = 10000
) -> Optional[pd.DataFrame]:
    client = get_cdf_client()
    if client is None:
        return None
    try:
        ts_id = _resolve_ts_id(client, ts_name_or_id)
        if ts_id is None:
            return None
        datapoints = client.time_series.data.retrieve(
            id=ts_id,
            start=start_time,
            end=end_time,
            limit=limit
        )
        df = datapoints.to_pandas()
        if df.empty:
            return None
        df.columns = ['value']
        df = df.reset_index()
        df.columns = ['timestamp', 'value']
        return df
    except Exception as e:
        import streamlit as st
        st.warning(f"Failed to fetch raw data for {ts_name_or_id}: {e}")
        return None


def fetch_flare_live_data(
    flare_id: str,
    start_time: datetime,
    end_time: datetime,
    sampling_rate: str = "1h"
) -> Dict[str, pd.DataFrame]:
    live_tags = get_live_tags(flare_id)
    result = {}
    for tag_type, ts_identifier in live_tags.items():
        df = fetch_timeseries_data(ts_identifier, start_time, end_time, sampling_rate)
        if df is not None:
            result[tag_type] = df
    return result


def get_cdf_connection_status() -> Tuple[bool, str]:
    if not CDF_AVAILABLE:
        return False, "CDF SDK not available"
    client = get_cdf_client()
    if client is None:
        return False, "Unable to connect to CDF"
    try:
        status = client.iam.token.inspect()
        project = status.projects[0].url_name if status.projects else "unknown"
        return True, f"Connected to project: {project}"
    except Exception as e:
        return False, f"Connection error: {e}"


def test_tag_access(ts_name_or_id) -> Tuple[bool, str]:
    client = get_cdf_client()
    if client is None:
        return False, "CDF client not available"
    try:
        ts_id = _resolve_ts_id(client, ts_name_or_id)
        if ts_id:
            ts = client.time_series.retrieve(id=ts_id)
            return True, f"Tag accessible: {ts.name} (id={ts.id})"
        return False, f"Tag not found: {ts_name_or_id}"
    except Exception as e:
        return False, f"Error accessing tag: {e}"
