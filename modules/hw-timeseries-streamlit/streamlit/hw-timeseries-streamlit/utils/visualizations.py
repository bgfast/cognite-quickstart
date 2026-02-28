"""
Visualization Module - interactive charts for emission data
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional, List


def create_hrvoc_chart(df: pd.DataFrame, flare_name: str = "") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['total_hrvoc'], mode='lines', name='Total HRVOC',
        line=dict(color='#DC3545', width=2),
        hovertemplate='<b>%{fullData.name}</b><br>Time: %{x}<br>HRVOC: %{y:.2f} lbs/hr<extra></extra>'
    ))
    fig.update_layout(
        title=f'HRVOC Trend - {flare_name}' if flare_name else 'HRVOC Trend',
        xaxis_title='Time', yaxis_title='HRVOC (lbs/hr)',
        hovermode='x unified', height=400, template='plotly_white'
    )
    return fig


def create_composition_chart(df: pd.DataFrame, flare_name: str = "") -> go.Figure:
    fig = go.Figure()
    colors = {'nitrogen_pct': '#87CEEB', 'co2_pct': '#808080', 'methane_pct': '#90EE90', 'ethane_pct': '#228B22', 'other_voc_pct': '#A0522D'}
    labels = {'nitrogen_pct': 'Nitrogen', 'co2_pct': 'CO2', 'methane_pct': 'Methane', 'ethane_pct': 'Ethane', 'other_voc_pct': 'Other VOCs'}
    for col in ['nitrogen_pct', 'co2_pct', 'methane_pct', 'ethane_pct', 'other_voc_pct']:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df['timestamp'], y=df[col], mode='lines', name=labels[col], stackgroup='one',
                fillcolor=colors[col], line=dict(width=0.5, color=colors[col]),
                hovertemplate=f'<b>{labels[col]}</b><br>Time: %{{x}}<br>Percentage: %{{y:.2f}}%<extra></extra>'
            ))
    fig.update_layout(
        title=f'Gas Composition - {flare_name}' if flare_name else 'Gas Composition',
        xaxis_title='Time', yaxis_title='Percentage (%)',
        hovermode='x unified', height=400, template='plotly_white', yaxis=dict(range=[0, 100])
    )
    return fig


def create_flow_heat_chart(df: pd.DataFrame, flare_name: str = "") -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['flow_rate'], mode='lines', name='Flow Rate', line=dict(color='#0066CC', width=2),
        hovertemplate='<b>Flow Rate</b><br>Time: %{x}<br>Flow: %{y:,.0f} scf/hr<extra></extra>'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['heat_value'], mode='lines', name='Heat Value', line=dict(color='#FF8800', width=2),
        hovertemplate='<b>Heat Value</b><br>Time: %{x}<br>Heat: %{y:.0f} BTU/scf<extra></extra>'), secondary_y=True)
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Flow Rate (scf/hr)", secondary_y=False)
    fig.update_yaxes(title_text="Heat Value (BTU/scf)", secondary_y=True)
    fig.update_layout(title=f'Flow Rate & Heat Value - {flare_name}' if flare_name else 'Flow Rate & Heat Value',
        hovermode='x unified', height=400, template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def create_mass_emissions_chart(df: pd.DataFrame, flare_name: str = "") -> go.Figure:
    fig = go.Figure()
    colors = {'nitrogen_mass': '#87CEEB', 'co2_mass': '#808080', 'methane_mass': '#90EE90', 'ethane_mass': '#228B22', 'other_voc_mass': '#A0522D'}
    labels = {'nitrogen_mass': 'Nitrogen', 'co2_mass': 'CO2', 'methane_mass': 'Methane', 'ethane_mass': 'Ethane', 'other_voc_mass': 'Other VOCs'}
    for col in ['nitrogen_mass', 'co2_mass', 'methane_mass', 'ethane_mass', 'other_voc_mass']:
        if col in df.columns:
            fig.add_trace(go.Bar(x=df['timestamp'], y=df[col], name=labels[col], marker_color=colors[col],
                hovertemplate=f'<b>{labels[col]}</b><br>Time: %{{x}}<br>Mass: %{{y:.2f}} lbs/hr<extra></extra>'))
    fig.update_layout(title=f'Mass Emissions by Component - {flare_name}' if flare_name else 'Mass Emissions by Component',
        xaxis_title='Time', yaxis_title='Mass Emission (lbs/hr)', barmode='stack',
        hovermode='x unified', height=400, template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig


def create_hrvoc_heat_release_chart(df: pd.DataFrame, flare_name: str = "") -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['total_hrvoc'], mode='lines', name='Total HRVOC', line=dict(color='#DC3545', width=2),
        hovertemplate='<b>Total HRVOC</b><br>Time: %{x}<br>HRVOC: %{y:.2f} lbs/hr<extra></extra>'), secondary_y=False)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['total_heat_release'], mode='lines', name='Total Heat Release', line=dict(color='#6F42C1', width=2),
        hovertemplate='<b>Total Heat Release</b><br>Time: %{x}<br>Heat: %{y:.4f} MMBTU/hr<extra></extra>'), secondary_y=True)
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="HRVOC (lbs/hr)", secondary_y=False)
    fig.update_yaxes(title_text="Heat Release (MMBTU/hr)", secondary_y=True)
    fig.update_layout(title=f'HRVOC & Heat Release - {flare_name}' if flare_name else 'HRVOC & Heat Release',
        hovermode='x unified', height=400, template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig
