"""
Tag lookup for HW Time Series Streamlit.
Maps data sources to CDF time series. Use external_ids from scripts/populate_edr_timeseries.py
(prefix: edr_training_). Source IDs (e.g. FLARE_BP1_001) are internal; display names are generic.
"""

from typing import Dict, List, Optional

EXTERNAL_ID_PREFIX = "edr_training_"

FLARE_TAG_LOOKUP: Dict[str, Dict] = {
    "FLARE_BP1_001": {
        "name": "Source 1",
        "unit": "Unit A",
        "location": "Site A",
        "description": "Demo source 1 - data from CDF time series (populate_edr_timeseries.py)",
        "tags": {
            "flow_rate": {
                "ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_flow_rate",
                "ts_id": None,
                "description": "Flow rate",
                "unit": "scf/hr",
                "source": "live",
            },
            "heat_value": {
                "ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_heat_value",
                "ts_id": None,
                "description": "Heat value",
                "unit": "BTU/scf",
                "source": "live",
            },
            "nitrogen": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_nitrogen_pct", "ts_id": None, "source": "live"},
            "co2": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_co2_pct", "ts_id": None, "source": "live"},
            "methane": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_methane_pct", "ts_id": None, "source": "live"},
            "ethane": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_ethane_pct", "ts_id": None, "source": "live"},
            "other_voc": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP1_001_other_voc_pct", "ts_id": None, "source": "live"},
        },
        "mock_data": {
            "flow_rate_range": [12000, 27000],
            "heat_value_range": [830, 920],
            "composition": {
                "nitrogen_range": [11.96, 13.02],
                "co2_range": [0.35, 0.46],
                "methane_range": [78.16, 81.53],
                "ethane_range": [2.15, 2.35],
                "other_voc_range": [0.5, 2.0],
            },
        },
    },
    "FLARE_BP2_001": {
        "name": "Source 2",
        "unit": "Unit B",
        "location": "Site B",
        "description": "Demo source 2 - data from CDF time series",
        "tags": {
            "flow_rate": {
                "ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_flow_rate",
                "ts_id": None,
                "description": "Flow rate",
                "unit": "scf/hr",
                "source": "live",
            },
            "heat_value": {
                "ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_heat_value",
                "ts_id": None,
                "description": "Heat value",
                "unit": "BTU/scf",
                "source": "live",
            },
            "nitrogen": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_nitrogen_pct", "ts_id": None, "source": "live"},
            "co2": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_co2_pct", "ts_id": None, "source": "live"},
            "methane": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_methane_pct", "ts_id": None, "source": "live"},
            "ethane": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_ethane_pct", "ts_id": None, "source": "live"},
            "other_voc": {"ts_identifier": f"{EXTERNAL_ID_PREFIX}FLARE_BP2_001_other_voc_pct", "ts_id": None, "source": "live"},
        },
        "mock_data": {
            "flow_rate_range": [15000, 30000],
            "heat_value_range": [840, 910],
            "composition": {
                "nitrogen_range": [12.0, 13.0],
                "co2_range": [0.36, 0.45],
                "methane_range": [78.5, 81.0],
                "ethane_range": [2.20, 2.40],
                "other_voc_range": [0.6, 2.2],
            },
        },
    },
}


def get_flare_config(flare_id: str) -> Optional[Dict]:
    return FLARE_TAG_LOOKUP.get(flare_id)


def get_all_flares() -> List[Dict]:
    flares = []
    for flare_id, config in FLARE_TAG_LOOKUP.items():
        flares.append({
            "id": flare_id,
            "name": config["name"],
            "unit": config["unit"],
            "location": config["location"],
            "description": config["description"],
            "mock_data": config.get("mock_data", {}),
        })
    return flares


def get_live_tags(flare_id: str) -> Dict[str, any]:
    config = get_flare_config(flare_id)
    if not config:
        return {}
    live_tags = {}
    for tag_name, tag_config in config.get("tags", {}).items():
        if tag_config.get("source") == "live":
            ts_id = tag_config.get("ts_id")
            ts_identifier = tag_config.get("ts_identifier")
            if ts_id:
                live_tags[tag_name] = ts_id
            elif ts_identifier:
                live_tags[tag_name] = ts_identifier
    return live_tags


def get_tag_identifier(flare_id: str, tag_type: str):
    config = get_flare_config(flare_id)
    if not config:
        return None
    tag_config = config.get("tags", {}).get(tag_type)
    if tag_config and tag_config.get("source") == "live":
        ts_id = tag_config.get("ts_id")
        if ts_id:
            return ts_id
        return tag_config.get("ts_identifier")
    return None


def get_tag_external_id(flare_id: str, tag_type: str) -> Optional[str]:
    return get_tag_identifier(flare_id, tag_type)


def is_tag_live(flare_id: str, tag_type: str) -> bool:
    config = get_flare_config(flare_id)
    if not config:
        return False
    tag_config = config.get("tags", {}).get(tag_type)
    if not tag_config:
        return False
    if tag_config.get("source") == "live":
        return bool(tag_config.get("ts_id") or tag_config.get("ts_identifier"))
    return False


def get_tag_summary() -> Dict:
    summary = {"total_flares": len(FLARE_TAG_LOOKUP), "flares": []}
    for flare_id, config in FLARE_TAG_LOOKUP.items():
        live_count = sum(1 for t in config.get("tags", {}).values() if t.get("source") == "live" and (t.get("ts_id") or t.get("ts_identifier")))
        mock_count = len(config.get("tags", {})) - live_count
        summary["flares"].append({
            "id": flare_id,
            "name": config["name"],
            "live_tags": live_count,
            "mock_tags": mock_count,
        })
    return summary
