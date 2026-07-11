"""
Industry page component.
Renders target industry analysis, treemaps of financial loss, and industry heatmaps.
"""

import streamlit as st
from typing import Dict, Any
import pandas as pd
import plotly.express as px

from frontend.components import render_industry_treemap
from backend.risk import get_industry_risk_scores
from frontend.layout import PLOTLY_THEME_LAYOUT, COLOR_PALETTE

def render(datasets: Dict[str, pd.DataFrame], filters: Dict[str, Any]):
    """Renders the Industry dashboard page."""
    st.markdown("<h1>🏢 Target Industry Analysis</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='font-size: 1.1rem; color: #8c9ba5; margin-bottom: 30px;'>"
        "Identify which commercial and government sectors face the highest financial impacts and risk exposures."
        "</p>",
        unsafe_allow_html=True
    )
    
    global_df = datasets["global_threats"]
    
    if global_df.empty:
        st.warning("No data matches the selected filters. Please adjust the sidebar choices.")
        return
        
    # 1. Calculate Industry Risk Scores
    industry_risk = get_industry_risk_scores(global_df)
    
    # 2. Render Treemap
    st.subheader("Industry Financial Loss Distribution")
    fig_tree = render_industry_treemap(industry_risk)
    st.plotly_chart(fig_tree, use_container_width=True)
    
    # 3. Two columns for Industry Heatmap & Detail List
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Industry Risk Leaderboard")
        display_df = industry_risk.rename(columns={
            "target_industry": "Industry",
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
        st.subheader("Attack Vectors by Target Sector")
        if "target_industry" in global_df.columns and "standard_attack_type" in global_df.columns:
            pivot_sectors = global_df.groupby(["target_industry", "standard_attack_type"]).size().unstack(fill_value=0)
            
            fig_heatmap = px.imshow(
                pivot_sectors,
                labels=dict(x="Attack Vector", y="Target Industry", color="Incident Count"),
                color_continuous_scale=[[0.0, "rgba(17, 25, 40, 0.6)"], [1.0, COLOR_PALETTE["neon_pink"]]],
                title="Sector Density Matrix of Attack Types"
            )
            fig_heatmap.update_layout(**PLOTLY_THEME_LAYOUT, height=350, margin={"t": 40, "b": 30, "l": 30, "r": 30})
            st.plotly_chart(fig_heatmap, use_container_width=True)
