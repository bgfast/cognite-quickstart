"""
HW Time Series Streamlit - Time Series Dashboard
Reads from CDF time series populated by scripts/populate_edr_timeseries.py.
Generic demo app (no customer-specific naming).
"""

# Version tracking for deployment verification (update when deploying changes)
VERSION = "2025.02.26.v1"

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os
import plotly.graph_objects as go

sys.path.append(os.path.dirname(__file__))

from utils.mock_data import generate_mock_flares, generate_mock_flare_data
from utils.calculations import calculate_emissions, load_calculation_params
from utils.visualizations import (
    create_hrvoc_chart,
    create_composition_chart,
    create_flow_heat_chart,
    create_mass_emissions_chart,
    create_hrvoc_heat_release_chart,
)
from utils.tag_lookup import FLARE_TAG_LOOKUP, get_tag_summary, get_live_tags
from utils.cdf_data import get_cdf_connection_status

st.set_page_config(
    page_title=f"HW Time Series Streamlit v{VERSION}",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .metric-card { background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #0066CC; }
    .stMetric { background-color: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def get_flare_data(flare_id: str, start_time: datetime, end_time: datetime, sampling_rate: str = "1h"):
    df = generate_mock_flare_data(flare_id, start_time, end_time, sampling_rate)
    df = calculate_emissions(df)
    return df


def get_time_range(period: str) -> tuple:
    end_time = datetime.now()
    if period == "24h":
        start_time = end_time - timedelta(days=1)
        sampling_rate = "15min"
    elif period == "7d":
        start_time = end_time - timedelta(days=7)
        sampling_rate = "1h"
    elif period == "30d":
        start_time = end_time - timedelta(days=30)
        sampling_rate = "1h"
    elif period == "90d":
        start_time = end_time - timedelta(days=90)
        sampling_rate = "1d"
    else:
        start_time = end_time - timedelta(days=7)
        sampling_rate = "1h"
    return start_time, end_time, sampling_rate


def dashboard_overview():
    st.header("🌍 Time Series Dashboard")
    with st.sidebar:
        st.header("Filters")
        time_period = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"], index=1)
        period_map = {"Last 24 Hours": "24h", "Last 7 Days": "7d", "Last 30 Days": "30d", "Last 90 Days": "90d"}
        period_value = period_map[time_period]
        flares = generate_mock_flares()
        units = ["All Units"] + sorted(list(set([f['unit'] for f in flares])))
        selected_unit = st.selectbox("Unit", units)
        filtered_flares = flares if selected_unit == "All Units" else [f for f in flares if f['unit'] == selected_unit]

    start_time, end_time, sampling_rate = get_time_range(period_value)
    st.subheader("Summary Metrics")
    total_hrvoc = total_heat_release = active_flares = 0
    data_quality = []
    for flare in filtered_flares:
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_hrvoc' in df.columns and 'total_heat_release' in df.columns:
                total_hrvoc += df['total_hrvoc'].sum()
                total_heat_release += df['total_heat_release'].sum()
                active_flares += 1
                quality_pct = (1 - df['flow_rate'].isna().sum() / len(df)) * 100
                data_quality.append(quality_pct)
        except Exception as e:
            st.error(f"Error loading data for {flare['name']}: {e}")
    avg_data_quality = np.mean(data_quality) if data_quality else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total HRVOC", f"{total_hrvoc:,.0f} lbs", delta=f"{period_value} period")
    with col2:
        st.metric("Total Heat Release", f"{total_heat_release:,.2f} MMBTU", delta=f"{period_value} period")
    with col3:
        st.metric("Active Sources", active_flares, delta=f"of {len(filtered_flares)} total")
    with col4:
        st.metric("Data Quality", f"{avg_data_quality:.1f}%", delta="completeness", delta_color="normal" if avg_data_quality >= 95 else "off")

    st.divider()
    st.subheader("Aggregate Trends")
    fig_hrvoc = go.Figure()
    for flare in filtered_flares:
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_hrvoc' in df.columns:
                fig_hrvoc.add_trace(go.Scatter(x=df['timestamp'], y=df['total_hrvoc'], mode='lines', name=flare['name'],
                    hovertemplate=f'<b>{flare["name"]}</b><br>Time: %{{x}}<br>HRVOC: %{{y:.2f}} lbs/hr<extra></extra>'))
        except Exception:
            continue
    fig_hrvoc.update_layout(title='Multi-Source HRVOC Trend', xaxis_title='Time', yaxis_title='HRVOC (lbs/hr)', hovermode='x unified', height=400, template='plotly_white')
    st.plotly_chart(fig_hrvoc, use_container_width=True)

    fig_heat = go.Figure()
    for flare in filtered_flares:
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_heat_release' in df.columns:
                fig_heat.add_trace(go.Scatter(x=df['timestamp'], y=df['total_heat_release'], mode='lines', name=flare['name'],
                    hovertemplate=f'<b>{flare["name"]}</b><br>Time: %{{x}}<br>Heat Release: %{{y:.4f}} MMBTU/hr<extra></extra>'))
        except Exception:
            continue
    fig_heat.update_layout(title='Multi-Source Heat Release Trend', xaxis_title='Time', yaxis_title='Heat Release (MMBTU/hr)', hovermode='x unified', height=400, template='plotly_white')
    st.plotly_chart(fig_heat, use_container_width=True)

    st.divider()
    st.subheader("Source Summary")
    summary_data = []
    for flare in filtered_flares:
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_hrvoc' in df.columns and 'total_heat_release' in df.columns:
                current_hrvoc = df['total_hrvoc'].sum()
                current_heat = df['total_heat_release'].sum()
                total_hrvoc_all = sum([get_flare_data(f['id'], start_time, end_time, sampling_rate)['total_hrvoc'].sum() for f in filtered_flares if not get_flare_data(f['id'], start_time, end_time, sampling_rate).empty])
                pct_of_total = (current_hrvoc / total_hrvoc_all * 100) if total_hrvoc_all > 0 else 0
                summary_data.append({'Source Name': flare['name'], 'Unit': flare['unit'], 'HRVOC (Current)': f"{current_hrvoc:,.0f} lbs", 'Heat Release (Current)': f"{current_heat:,.2f} MMBTU", '% of Total': f"{pct_of_total:.1f}%", 'Status': 'Active'})
        except Exception:
            continue
    if summary_data:
        st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for selected filters.")


def flare_detail():
    st.header("🔍 Source Detail View")
    flares = generate_mock_flares()
    flare_names = [f"{f['name']} ({f['unit']})" for f in flares]
    with st.sidebar:
        selected_flare_name = st.selectbox("Select Source", flare_names)
        selected_flare = flares[flare_names.index(selected_flare_name)]
        time_period = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"], index=1)
        period_value = {"Last 24 Hours": "24h", "Last 7 Days": "7d", "Last 30 Days": "30d", "Last 90 Days": "90d"}[time_period]
    start_time, end_time, sampling_rate = get_time_range(period_value)
    st.subheader(f"{selected_flare['name']}")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Unit:** {selected_flare['unit']}")
        st.write(f"**Location:** {selected_flare['location']}")
    with col2:
        st.write(f"**Description:** {selected_flare['description']}")
        st.write("**Status:** Active")
    st.divider()
    try:
        df = get_flare_data(selected_flare['id'], start_time, end_time, sampling_rate)
        if df.empty:
            st.warning("No data available for selected source and time period.")
            return
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current HRVOC", f"{df['total_hrvoc'].iloc[-1]:.2f} lbs/hr" if not df.empty else "0")
        with col2:
            st.metric("Current Heat Release", f"{df['total_heat_release'].iloc[-1]:.4f} MMBTU/hr" if not df.empty else "0")
        with col3:
            st.metric("Average Flow Rate", f"{df['flow_rate'].mean():,.0f} scf/hr" if 'flow_rate' in df.columns else "0")
        with col4:
            st.metric("Average Heat Value", f"{df['heat_value'].mean():.0f} BTU/scf" if 'heat_value' in df.columns else "0")
        st.divider()
        st.subheader("Time Series Charts")
        st.plotly_chart(create_flow_heat_chart(df, selected_flare['name']), use_container_width=True)
        st.plotly_chart(create_composition_chart(df, selected_flare['name']), use_container_width=True)
        st.plotly_chart(create_mass_emissions_chart(df, selected_flare['name']), use_container_width=True)
        st.plotly_chart(create_hrvoc_heat_release_chart(df, selected_flare['name']), use_container_width=True)
        st.divider()
        st.subheader("Detailed Data")
        display_cols = ['timestamp', 'flow_rate', 'heat_value', 'tmfr', 'nitrogen_pct', 'co2_pct', 'methane_pct', 'ethane_pct', 'other_voc_pct',
            'nitrogen_adj', 'co2_adj', 'methane_adj', 'ethane_adj', 'other_voc_adj', 'nhv_total_calc', 'de_1', 'de_2',
            'nitrogen_mass', 'co2_mass', 'methane_mass', 'ethane_mass', 'other_voc_mass', 'total_hrvoc', 'total_heat_release']
        available_cols = [c for c in display_cols if c in df.columns]
        display_df = df[available_cols].copy()
        for col in display_df.select_dtypes(include=[np.number]).columns:
            if 'pct' in col or 'adj' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
            elif 'mass' in col or 'hrvoc' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
            elif 'heat_release' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
            elif 'nhv' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
            elif 'de_' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x*100:.1f}%" if pd.notna(x) else "")
            elif 'tmfr' in col:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.6f}" if pd.notna(x) else "")
            else:
                display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", data=csv, file_name=f"{selected_flare['id']}_{period_value}_data.csv", mime="text/csv")
    except Exception as e:
        st.error(f"Error loading source data: {e}")
        import traceback
        st.code(traceback.format_exc())


def comparison_view():
    st.header("📊 Source Comparison")
    flares = generate_mock_flares()
    flare_names = [f"{f['name']} ({f['unit']})" for f in flares]
    with st.sidebar:
        selected_flares = st.multiselect("Select Sources to Compare", flare_names, default=flare_names[:2] if len(flare_names) >= 2 else flare_names)
        time_period = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"], index=1)
        period_value = {"Last 24 Hours": "24h", "Last 7 Days": "7d", "Last 30 Days": "30d", "Last 90 Days": "90d"}[time_period]
    if not selected_flares:
        st.warning("Please select at least one source to compare.")
        return
    start_time, end_time, sampling_rate = get_time_range(period_value)
    st.subheader("HRVOC by Source")
    fig_hrvoc = go.Figure()
    for flare_name in selected_flares:
        flare = flares[flare_names.index(flare_name)]
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_hrvoc' in df.columns:
                fig_hrvoc.add_trace(go.Scatter(x=df['timestamp'], y=df['total_hrvoc'], mode='lines', name=flare['name'],
                    hovertemplate=f'<b>{flare["name"]}</b><br>Time: %{{x}}<br>HRVOC: %{{y:.2f}} lbs/hr<extra></extra>'))
        except Exception:
            continue
    fig_hrvoc.update_layout(title='HRVOC Comparison', xaxis_title='Time', yaxis_title='HRVOC (lbs/hr)', hovermode='x unified', height=400, template='plotly_white')
    st.plotly_chart(fig_hrvoc, use_container_width=True)
    st.subheader("Heat Release by Source")
    fig_heat = go.Figure()
    for flare_name in selected_flares:
        flare = flares[flare_names.index(flare_name)]
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty and 'total_heat_release' in df.columns:
                fig_heat.add_trace(go.Scatter(x=df['timestamp'], y=df['total_heat_release'], mode='lines', name=flare['name'],
                    hovertemplate=f'<b>{flare["name"]}</b><br>Time: %{{x}}<br>Heat Release: %{{y:.4f}} MMBTU/hr<extra></extra>'))
        except Exception:
            continue
    fig_heat.update_layout(title='Heat Release Comparison', xaxis_title='Time', yaxis_title='Heat Release (MMBTU/hr)', hovermode='x unified', height=400, template='plotly_white')
    st.plotly_chart(fig_heat, use_container_width=True)
    st.divider()
    st.subheader("Comparison Summary")
    comparison_data = []
    for flare_name in selected_flares:
        flare = flares[flare_names.index(flare_name)]
        try:
            df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
            if not df.empty:
                comparison_data.append({'Source': flare['name'], 'Unit': flare['unit'], 'Total HRVOC': f"{df['total_hrvoc'].sum():,.0f} lbs", 'Total Heat Release': f"{df['total_heat_release'].sum():,.2f} MMBTU", 'Avg Flow Rate': f"{df['flow_rate'].mean():,.0f} scf/hr", 'Avg Heat Value': f"{df['heat_value'].mean():.0f} BTU/scf"})
        except Exception:
            continue
    if comparison_data:
        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
    else:
        st.info("No data available for selected sources.")


def reporting_page():
    st.header("📄 Reporting & Export")
    flares = generate_mock_flares()
    flare_names = [f"{f['name']} ({f['unit']})" for f in flares]
    with st.form("report_config"):
        st.subheader("Report Configuration")
        col1, col2 = st.columns(2)
        with col1:
            report_type = st.selectbox("Report Type", ["Daily", "Weekly", "Monthly", "Custom"])
            selected_flares_report = st.multiselect("Select Sources", flare_names, default=flare_names)
        with col2:
            time_period = st.selectbox("Time Period", ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"], index=1)
            metrics = st.multiselect("Metrics to Include", ["HRVOC", "Heat Release", "Flow Rate", "Gas Composition", "Mass Emissions"], default=["HRVOC", "Heat Release", "Flow Rate"])
        submitted = st.form_submit_button("Generate Report")
    if submitted:
        if not selected_flares_report:
            st.warning("Please select at least one source.")
        elif not metrics:
            st.warning("Please select at least one metric.")
        else:
            period_value = {"Last 24 Hours": "24h", "Last 7 Days": "7d", "Last 30 Days": "30d", "Last 90 Days": "90d"}[time_period]
            start_time, end_time, sampling_rate = get_time_range(period_value)
            report_data = []
            for flare_name in selected_flares_report:
                flare = flares[flare_names.index(flare_name)]
                try:
                    df = get_flare_data(flare['id'], start_time, end_time, sampling_rate)
                    if not df.empty:
                        report_data.append({'Source': flare['name'], 'Unit': flare['unit'], 'Total HRVOC (lbs)': df['total_hrvoc'].sum() if 'HRVOC' in metrics else None, 'Total Heat Release (MMBTU)': df['total_heat_release'].sum() if 'Heat Release' in metrics else None, 'Avg Flow Rate (scf/hr)': df['flow_rate'].mean() if 'Flow Rate' in metrics else None})
                except Exception:
                    continue
            if report_data:
                report_df = pd.DataFrame(report_data)
                st.subheader("Report Preview")
                st.dataframe(report_df, use_container_width=True, hide_index=True)
                csv = report_df.to_csv(index=False)
                st.download_button("Download CSV", data=csv, file_name=f"timeseries_report_{report_type.lower()}_{period_value}.csv", mime="text/csv")
            else:
                st.warning("No data available for selected configuration.")


def tag_configuration():
    st.header("⚙️ Tag Configuration")
    st.subheader("CDF Connection Status")
    is_connected, status_msg = get_cdf_connection_status()
    if is_connected:
        st.success(f"✅ {status_msg}")
    else:
        st.warning(f"⚠️ {status_msg} - Using mock data for all tags")
    st.divider()
    st.subheader("Tag Configuration Summary")
    summary = get_tag_summary()
    summary_data = [{"Source ID": f["id"], "Source Name": f["name"], "Live Tags": f["live_tags"], "Mock Tags": f["mock_tags"], "Status": "🟢 Partial Live" if f["live_tags"] > 0 else "🟡 All Mock"} for f in summary["flares"]]
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
    st.divider()
    st.subheader("Detailed Tag Lookup Table")
    for flare_id, config in FLARE_TAG_LOOKUP.items():
        with st.expander(f"📊 {config['name']} ({config['unit']})"):
            st.write(f"**Unit:** {config['unit']}")
            st.write("**Tag Mappings:**")
            tag_data = []
            for tag_name, tag_config in config.get("tags", {}).items():
                source = tag_config.get("source", "mock")
                ts_identifier = tag_config.get("ts_identifier")
                is_live = source == "live" and ts_identifier
                tag_data.append({"Tag Type": tag_name, "TS Identifier": str(ts_identifier) if ts_identifier else "Not configured", "Source": "🟢 LIVE" if is_live else "🟡 MOCK", "Unit": tag_config.get("unit", ""), "Description": tag_config.get("description", "")})
            st.dataframe(pd.DataFrame(tag_data), use_container_width=True, hide_index=True)
    st.info("Time series are populated by running: python scripts/populate_edr_timeseries.py")


def main():
    pages = {"Dashboard": dashboard_overview, "Source Details": flare_detail, "Comparison": comparison_view, "Reporting": reporting_page, "Tag Configuration": tag_configuration}
    selected_page = st.sidebar.selectbox("Navigation", list(pages.keys()))
    st.sidebar.divider()
    st.sidebar.write(f"**Version**: {VERSION}")
    st.sidebar.markdown("**Data Sources:**")
    is_connected, _ = get_cdf_connection_status()
    if is_connected:
        st.sidebar.success("🟢 CDF Connected")
    else:
        st.sidebar.warning("🟡 Mock Data Only")
    pages[selected_page]()


if __name__ == "__main__":
    main()
