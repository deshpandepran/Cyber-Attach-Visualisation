"""
Country Map page component.
Renders the interactive world choropleth map and list of Country Risk Scores.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd
import plotly.express as px

from frontend.components import render_risk_choropleth
from backend.risk import get_country_risk_scores
from frontend.layout import PLOTLY_THEME_LAYOUT, COLOR_PALETTE

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Country Map & Risk Index page."""
    st.markdown("<h1>🗺️ Global Threat Risk Index</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Observe geographic distribution of cyber attacks and evaluate normalized national Risk Indexes."
        "</p>",
        unsafe_allow_html=True
    )
    
    global_df = datasets["global_threats"]
    
    if global_df.empty:
        st.warning("No data matches the selected filters. Please adjust the sidebar choices.")
        return
        
    # 1. Calculate Country Risk Scores
    risk_df = get_country_risk_scores(global_df)
    
    # 2. Render Choropleth Map
    fig_map = render_risk_choropleth(risk_df)
    st.plotly_chart(fig_map, use_container_width=True)
    
    # 3. Two columns for Detail Table and Country Comparison
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("National Risk Matrix Details")
        display_df = risk_df.rename(columns={
            "standard_country": "Country",
            "incident_count": "Incident Count",
            "avg_loss": "Avg Financial Loss ($M)",
            "avg_resolution_time": "Avg Resolution (Hrs)",
            "risk_score": "Risk Index"
        })
        st.dataframe(
            display_df.style.format({
                "Avg Financial Loss ($M)": "${:,.2f}M",
                "Avg Resolution (Hrs)": "{:,.1f} hrs",
                "Risk Index": "{:,.2f}"
            }),
            use_container_width=True,
            hide_index=True
        )
        
    with col2:
        st.subheader("Risk Score Leaderboard")
        fig_bar = px.bar(
            risk_df,
            x="risk_score",
            y="standard_country",
            orientation="h",
            color="risk_score",
            color_continuous_scale=[[0.0, "rgba(17, 25, 40, 0.6)"], [1.0, COLOR_PALETTE["neon_pink"]]],
            labels={"risk_score": "Risk Score", "standard_country": "Country"},
            title="Countries Ranked by Risk Score"
        )
        fig_bar.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
        st.plotly_chart(fig_bar, use_container_width=True)
