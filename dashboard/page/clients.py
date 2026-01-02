import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from back.query.queries import get_clients_summary
from back.src.utils import apply_chart_style

# --- Data Enrichment ---
def enrich_client_data(df):
    """
    Adds mock metrics (LTV, Projects) but excludes Score/Tier as requested.
    """
    if df.empty: return df
    
    # Deterministic randomness based on client name
    # Deterministic randomness based on client name for active projects (if not available in DB, but DB count is best)
    # LTV is now real from 'get_clients_summary' query.
    
    # Keeping mock projects count if DB returns 0 for "total_orders" to avoid empty charts?
    # Actually the query joins order, so real count is used.
    # We might want to keep the churn risk logic.
    
    df['projects_active'] = df['total_orders'] # Use real order count as proxy for projects
    df['ltv'] = df['ltv'].astype(float) # Ensure float
    
    # Categorize Churn Risk based on 'projects_active' instead of score
    # Fewer projects = Higher risk (assumption)
    conditions = [
        (df['projects_active'] >= 4),
        (df['projects_active'] >= 2),
        (df['projects_active'] < 2)
    ]
    choices = ['Low', 'Medium', 'High']
    df['churn_risk'] = np.select(conditions, choices, default='Medium')
    
    return df

def render_growth_matrix(df):
    """Bubble chart: Projects Active vs LTV"""
    fig = px.scatter(
        df,
        x="projects_active",
        y="ltv",
        size="ltv",
        color="churn_risk",
        hover_name="name",
        text="name",
        title="Client Value Matrix",
        labels={"projects_active": "Active Projects", "ltv": "Lifetime Value (IDR)", "churn_risk": "Risk Profile"},
        color_discrete_map={"Low": "#2ecc71", "Medium": "#f1c40f", "High": "#e74c3c"},
        template="plotly_dark",
        size_max=40
    )
    fig.update_traces(textposition='top center')
    fig.update_traces(textposition='top center')
    apply_chart_style(fig)
    fig.update_layout(
        xaxis=dict(tickmode='linear', dtick=1),
        xaxis_title="Active Projects",
        yaxis_title="Lifetime Value (IDR)"
    )
    return fig

def render_map(df):
    """Clustered Map implementation"""
    m = folium.Map(location=[20, 10], zoom_start=2, tiles="CartoDB Dark Matter")
    marker_cluster = MarkerCluster().add_to(m)
    
    region_centers = {
        "Asia Pacific": [-2.5, 120.0],
        "Europe": [48.0, 10.0],
        "North America": [40.0, -100.0],
        "Middle East": [25.0, 45.0],
        "SE Asia": [3.0, 101.0],
        "Africa": [0.0, 20.0],
        "South America": [-15.0, -60.0]
    }
    
    import random
    for _, row in df.iterrows():
        region = row.get('region', 'Asia Pacific')
        center = region_centers.get(region, region_centers["Asia Pacific"])
        
        # Jitter
        lat = center[0] + random.uniform(-5.0, 5.0)
        lon = center[1] + random.uniform(-5.0, 5.0)
        
        # Color based on Churn Risk
        color_map = {"Low": "green", "Medium": "orange", "High": "red"}
        icon_color = color_map.get(row['churn_risk'], "blue")
        
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>{row['name']}</b><br>LTV: {row['ltv']/1e9:.1f}B IDR",
            tooltip=f"{row['name']} ({row['industry']})",
            icon=folium.Icon(color=icon_color, icon="user", prefix="fa")
        ).add_to(marker_cluster)
        
    st_folium(m, width=None, height=500, use_container_width=True, returned_objects=[])

def render_clients_page():
    st.markdown("## 🤝 Strategic Client Portfolio")
    st.caption("Advanced CRM Analysis & Distribution")

    # 1. Load & Enrich Data
    raw_df = get_clients_summary()
    if raw_df.empty:
        st.info("No client data loaded.")
        return
        
    df = enrich_client_data(raw_df)
    
    # 2. Executive Summary Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Clients", len(df), "+3% MoM")
    
    avg_prj = df['projects_active'].mean()
    c2.metric("Avg Active Projects", f"{avg_prj:.1f}", "Operational Load")
    
    high_value_sum = df[df['ltv'] > 3000000000]['ltv'].sum()
    c3.metric("High Value Pipeline", f"IDR {high_value_sum/1e9:.1f}B", "Key Accounts")
    
    at_risk = len(df[df['churn_risk'] == 'High'])
    c4.metric("Risk Alert (Low Activity)", at_risk, "Needs Engagement", delta_color="inverse")
    
    st.markdown("---")
    
    # 3. Interactive Tabs
    tab_matrix, tab_map, tab_list = st.tabs(["🚀 Value Matrix", "🌍 Geographic Presence", "📋 Directory"])
    
    with tab_matrix:
        c_chart, c_insight = st.columns([3, 1])
        with c_chart:
            st.plotly_chart(render_growth_matrix(df), use_container_width=True)
        with c_insight:
            st.markdown("#### 💡 Strategy Audit")
            st.info("**Key Partners**: Clients with many active projects and high LTV.")
            st.warning("**Potential Upsell**: Clients with high LTV but few active projects.")
            
    with tab_map:
        st.subheader("Global Client Footprint")
        render_map(df)
        
    with tab_list:
        # Search & Sort
        col_search, col_sort = st.columns([3, 1])
        text_search = col_search.text_input("🔍 Search Client", placeholder="Type name...")
        sort_opt = col_sort.selectbox("Sort By", ["LTV (High-Low)", "Projects (High-Low)", "Name (A-Z)"])

        filtered_df = df.copy()
        if text_search:
            filtered_df = filtered_df[filtered_df['name'].str.contains(text_search, case=False)]
            
        if sort_opt == "LTV (High-Low)":
            filtered_df = filtered_df.sort_values('ltv', ascending=False)
        elif sort_opt == "Projects (High-Low)":
            filtered_df = filtered_df.sort_values('projects_active', ascending=False)
        else:
            filtered_df = filtered_df.sort_values('name')
            
        st.dataframe(
            filtered_df[['name', 'industry', 'region', 'projects_active', 'ltv', 'churn_risk']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": "Client Name",
                "ltv": st.column_config.ProgressColumn("Lifetime Value (IDR)", min_value=0, max_value=int(df['ltv'].max()), format="IDR %d"),
                "churn_risk": st.column_config.Column("Risk Profile", width="small"),
                "projects_active": st.column_config.Column("Active Prj")
            }
        )
