"""
Emission calculation module.
Calculates mass emissions, HRVOC, and Heat Release from raw sensor/source data.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List


def load_calculation_params() -> Dict:
    config = {
        'molecular_weights': {
            'nitrogen': 28.01, 'co2': 44.01, 'methane': 16.04, 'ethane': 30.07,
            'ethylene': 28.05, 'propylene': 42.08, 'butadiene': 54.09,
            'butene_1': 56.11, 'trans_butene_2': 56.11, 'cis_butene_2': 56.11,
            'hydrogen': 2.02, 'carbon_monoxide': 28.01, 'propane': 44.10,
            'isobutane': 58.12, 'normal_butane': 58.12, 'c5plus': 72.15,
            'water': 18.02, 'dme': 46.07, 'ethylene_oxide': 44.05,
            'acetylene': 26.04, 'oxygen': 32.00, 'other_voc': 30.0
        },
        'nhv_btu_per_lb': {
            'ethylene': 20288, 'ethane': 20437, 'acetylene': 20774,
            'hydrogen_combustion': 231180, 'hydrogen_header': 51623,
            'methane': 21523, 'carbon_monoxide': 4347, 'propane': 19929,
            'isobutane': 19603, 'normal_butane': 19676, 'butene_1': 19481,
            'trans_butene_2': 19406, 'cis_butene_2': 19433, 'butadiene': 19162,
            'c5plus': 19519, 'propylene': 19686, 'dme': 12405, 'ethylene_oxide': 11895
        },
        'conversion_factors': {
            'scf_per_lbmole': 385.3, 'btu_to_mmbtu': 1000000,
            'scfs_to_scfhr': 3600, 'scfm_to_scfs': 60, 'seconds_to_hours': 3600
        },
        'destruction_efficiency': {
            'de_1': 0.01, 'de_2_high': 0.01, 'de_2_low': 0.02
        },
        'hrvoc_components': ['ethylene', 'propylene', 'butadiene', 'butene_1', 'trans_butene_2', 'cis_butene_2'],
        'aggregation': {'default_period': 'hourly', 'time_zone': 'America/Chicago'}
    }
    return config


def normalize_composition(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    comp_cols = [col for col in df.columns if col.endswith('_pct')]
    if not comp_cols:
        return df
    df['_composition_total'] = df[comp_cols].sum(axis=1)
    for col in comp_cols:
        adj_col = col.replace('_pct', '_adj')
        df[adj_col] = np.where(
            df['_composition_total'] > 0,
            df[col] * 100 / df['_composition_total'],
            df[col]
        )
    df = df.drop(columns=['_composition_total'])
    return df


def calculate_tmfr(flow_rate_scfhr: pd.Series) -> pd.Series:
    params = load_calculation_params()
    conversion_factors = params.get('conversion_factors', {})
    scf_per_lbmole = conversion_factors.get('scf_per_lbmole', 385.3)
    scfm_to_scfs = conversion_factors.get('scfm_to_scfs', 60)
    flow_rate_scfm = flow_rate_scfhr / 60
    flow_rate_scfs = flow_rate_scfm / scfm_to_scfs
    tmfr = flow_rate_scfs / scf_per_lbmole
    return tmfr


def calculate_nhv_from_composition(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    params = load_calculation_params()
    molecular_weights = params.get('molecular_weights', {})
    nhv_btu_per_lb = params.get('nhv_btu_per_lb', {})
    conversion_factors = params.get('conversion_factors', {})
    scf_per_lbmole = conversion_factors.get('scf_per_lbmole', 385.3)
    nhv_total = pd.Series(0.0, index=df.index)
    if 'methane_adj' in df.columns:
        nhv_ch4 = (df['methane_adj'] / 100) * molecular_weights.get('methane', 16.04) * nhv_btu_per_lb.get('methane', 21523) / scf_per_lbmole
        df['nhv_ch4'] = nhv_ch4
        nhv_total += nhv_ch4
    if 'ethane_adj' in df.columns:
        nhv_c2h6 = (df['ethane_adj'] / 100) * molecular_weights.get('ethane', 30.07) * nhv_btu_per_lb.get('ethane', 20437) / scf_per_lbmole
        df['nhv_c2h6'] = nhv_c2h6
        nhv_total += nhv_c2h6
    if 'co2_adj' in df.columns:
        df['nhv_co2'] = 0.0
    if 'nitrogen_adj' in df.columns:
        df['nhv_n2'] = 0.0
    if 'other_voc_adj' in df.columns:
        avg_nhv_btu_per_lb = (nhv_btu_per_lb.get('ethylene', 20288) + nhv_btu_per_lb.get('propylene', 19686) + nhv_btu_per_lb.get('propane', 19929)) / 3
        avg_mw = (molecular_weights.get('ethylene', 28.05) + molecular_weights.get('propylene', 42.08) + molecular_weights.get('propane', 44.10)) / 3
        nhv_other = (df['other_voc_adj'] / 100) * avg_mw * avg_nhv_btu_per_lb / scf_per_lbmole
        df['nhv_other_voc'] = nhv_other
        nhv_total += nhv_other
    df['nhv_total_calc'] = nhv_total
    return df


def calculate_destruction_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    params = load_calculation_params()
    de_config = params.get('destruction_efficiency', {})
    de_1_high = de_config.get('de_1', 0.01)
    de_2_high = de_config.get('de_2_high', 0.01)
    de_2_low = de_config.get('de_2_low', 0.02)
    if 'nhv_total_calc' in df.columns:
        df['de_1'] = de_1_high
        df['de_2'] = np.where(df['nhv_total_calc'] > 400, de_2_high, de_2_low)
    else:
        df['de_1'] = de_1_high
        df['de_2'] = de_2_low
    return df


def calculate_mass_emissions_redline(
    df: pd.DataFrame,
    molecular_weights: Optional[Dict] = None,
    conversion_factors: Optional[Dict] = None
) -> pd.DataFrame:
    if molecular_weights is None or conversion_factors is None:
        params = load_calculation_params()
        molecular_weights = params.get('molecular_weights', {})
        conversion_factors = params.get('conversion_factors', {})
    df = df.copy()
    df['tmfr'] = calculate_tmfr(df['flow_rate'])
    if 'de_1' not in df.columns or 'de_2' not in df.columns:
        df = calculate_destruction_efficiency(df)
    seconds_to_hours = conversion_factors.get('seconds_to_hours', 3600)
    if 'methane_adj' in df.columns:
        df['methane_mass'] = df['tmfr'] * (df['methane_adj'] / 100) * molecular_weights.get('methane', 16.04) * seconds_to_hours * df['de_1']
    if 'ethane_adj' in df.columns:
        df['ethane_mass'] = df['tmfr'] * (df['ethane_adj'] / 100) * molecular_weights.get('ethane', 30.07) * seconds_to_hours * df['de_1']
    if 'co2_adj' in df.columns:
        df['co2_mass'] = 0.0
    if 'nitrogen_adj' in df.columns:
        df['nitrogen_mass'] = 0.0
    if 'other_voc_adj' in df.columns:
        avg_mw = (molecular_weights.get('ethylene', 28.05) + molecular_weights.get('propylene', 42.08) + molecular_weights.get('propane', 44.10)) / 3
        df['other_voc_mass'] = df['tmfr'] * (df['other_voc_adj'] / 100) * avg_mw * seconds_to_hours * df['de_2']
    return df


def calculate_total_hrvoc_redline(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if 'other_voc_mass' in df.columns:
        df['total_hrvoc'] = df['other_voc_mass'] * 0.5
    else:
        df['total_hrvoc'] = 0.0
    return df


def calculate_heat_release_redline(
    df: pd.DataFrame,
    conversion_factors: Optional[Dict] = None
) -> pd.DataFrame:
    if conversion_factors is None:
        params = load_calculation_params()
        conversion_factors = params.get('conversion_factors', {})
    df = df.copy()
    if 'tmfr' not in df.columns:
        df['tmfr'] = calculate_tmfr(df['flow_rate'])
    if 'nhv_total_calc' not in df.columns:
        df = calculate_nhv_from_composition(df)
    scf_per_lbmole = conversion_factors.get('scf_per_lbmole', 385.3)
    seconds_to_hours = conversion_factors.get('seconds_to_hours', 3600)
    btu_to_mmbtu = conversion_factors.get('btu_to_mmbtu', 1000000)
    df['total_heat_release'] = df['tmfr'] * seconds_to_hours * scf_per_lbmole * df['nhv_total_calc'] / btu_to_mmbtu
    return df


def calculate_emissions(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_composition(df)
    df = calculate_nhv_from_composition(df)
    df = calculate_destruction_efficiency(df)
    df = calculate_mass_emissions_redline(df)
    df = calculate_total_hrvoc_redline(df)
    df = calculate_heat_release_redline(df)
    return df


def aggregate_by_period(df: pd.DataFrame, period: str = "daily") -> pd.DataFrame:
    if 'timestamp' in df.columns:
        df = df.set_index('timestamp')
    freq = {"hourly": "1H", "daily": "1D", "weekly": "1W", "monthly": "1M"}.get(period, "1D")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    return df[numeric_cols].resample(freq).sum().reset_index()
