import streamlit as st
import pandas as pd
import folium
import plotly.express as px
import plotly.graph_objects as go
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np

from back.query.queries import get_data_water
from back.src.utils import load_html

def page_heatmap(df, indikator):
    # Fallback to mock data if empty
    if df.empty:
        st.warning("⚠️ Data real tidak tersedia.", icon="⚠️")
        return

    # Check if indicator exists
    if indikator not in df.columns:
        st.error(f"❌ Indikator '{indikator}' tidak ditemukan dalam data.")
        return

    # Aggregate data by location (Average over selected time range)
    # This prevents heatmap intensity from exploding when selecting large date ranges
    df_agg = df.groupby(['latitude', 'longitude'], as_index=False)[indikator].mean()
    
    # Prepare heatmap data
    heat_data = df_agg[['latitude', 'longitude', indikator]].dropna().values.tolist()

    if not heat_data:
        st.warning(f"Data {indikator} kosong atau tidak valid.")
        return

    # Map Center
    avg_lat = df['latitude'].mean()
    avg_lon = df['longitude'].mean()
    
    # Base Map
    m = folium.Map(
        location=[avg_lat, avg_lon], 
        zoom_start=13, 
        tiles="CartoDB Dark Matter",
        control_scale=True
    )

    HeatMap(
        heat_data, 
        radius=25, 
        blur=20, 
        max_zoom=1,
        gradient={0.4: '#1e3a8a', 0.65: '#2dd4bf', 1: '#38bdf8'} # Aurora gradient (Deep Blue -> Teal -> Sky)
    ).add_to(m)
    
    # Render
    try:
        st_folium(m, height=400, use_container_width=True, returned_objects=[])
    except Exception as e:
        st.error(f"Gagal merender peta: {e}")

def radar_chart(df):
    with st.spinner("Menganalisis kondisi lingkungan..."):
        if df.empty:
            st.warning("Data kosong.")
            return
            
        metrics = ['salinitas', 'turbidity', 'current', 'oxygen', 'tide', 'density']
        
        # Filter available metrics
        available_metrics = [m for m in metrics if m in df.columns]
        
        if not available_metrics:
            st.warning("Metric lingkungan tidak lengkap.")
            return
        
        # Calculate averages
        avg_values = df[available_metrics].mean()
        
        # Configuration for Normalization & Limits
        ranges = {
            'salinitas': {'min': 0, 'max': 40, 'limit': 35},
            'turbidity': {'min': 0, 'max': 60, 'limit': 40},
            'current': {'min': 0, 'max': 3.0, 'limit': 2.0},
            'oxygen': {'min': 0, 'max': 10, 'limit': 4}, # Oxygen low is bad usually, but simplest viz for now
            'tide': {'min': 0, 'max': 3.0, 'limit': 2.5},
            'density': {'min': 1010, 'max': 1030, 'limit': 1027}
        }
        
        normalized_data = []
        limit_data_norm = []
        raw_data = []
        alerts = []
        
        for m in available_metrics:
            val = avg_values[m]
            conf = ranges.get(m, {'min': 0, 'max': val * 1.5, 'limit': val})
            
            # Normalize Value
            rn = conf['max'] - conf['min']
            pct = 0
            if rn != 0:
                pct = ((val - conf['min']) / rn) * 100
            pct = max(0, min(100, pct))
            normalized_data.append(pct)
            raw_data.append(val)
            
            # Normalize Limit
            limit_pct = 0
            if rn != 0:
                limit_pct = ((conf['limit'] - conf['min']) / rn) * 100
            limit_data_norm.append(limit_pct)
            
            # Check Alert (Simple logic: if > limit)
            # Note: For Oxygen, lower is usually worse, but for this demo we assume "Headroom" logic
            if val > conf['limit'] and m != 'oxygen':
                 alerts.append(f"{m.title()} High ({val:.1f})")
        
        # Labels
        labels = [m.title() for m in available_metrics]
        
        # Close the loop for Plotly Polar
        normalized_data_closed = normalized_data + [normalized_data[0]]
        limit_data_closed = limit_data_norm + [limit_data_norm[0]]
        labels_closed = labels + [labels[0]]
        
        # --- UI Summary ---
        # Calculate 'Stability Score'
        avg_stress = np.mean(normalized_data)
        health_score = max(0, 100 - avg_stress)
        
        if health_score > 70:
            status_color = "#4ade80" # Green 400
            status_text = "Optimal"
        elif health_score > 40:
            status_color = "#fbbf24" # Amber 400
            status_text = "Caution"
        else:
            status_color = "#f472b6" # Pink 400 (Trending Warning)
            status_text = "Critical"

        c1, c2 = st.columns([1, 2])
        with c1:
            html_content = load_html("health_score_card.html")
            
            if html_content:
                rendered_html = html_content.replace("{status_color}", status_color)\
                                            .replace("{health_score}", f"{health_score:.0f}")\
                                            .replace("{status_text}", status_text.upper())
                st.markdown(rendered_html, unsafe_allow_html=True)
            else:
                st.error("HTML Template not found")
            
            if alerts:
                st.markdown("##### ⚠️ Alerts")
                for a in alerts[:3]:
                    st.caption(f"• {a}")
            else:
                st.caption("✅ All systems nominal")

        with c2:
            fig = go.Figure()
    
            # Trace 1: Safe Limit
            fig.add_trace(go.Scatterpolar(
                r=limit_data_closed,
                theta=labels_closed,
                fill='none',
                name='Threshold',
                line=dict(color='rgba(255, 255, 255, 0.3)', width=1, dash='dash'),
                hoverinfo='skip',
                showlegend=True
            ))
    
            # Trace 2: Live Data
            fig.add_trace(go.Scatterpolar(
                r=normalized_data_closed,
                theta=labels_closed,
                fill='toself',
                name='Live Data',
                line=dict(color=status_color, width=3),
                fillcolor=f"rgba{tuple(int(status_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.3,)}", 
                marker=dict(size=8, color=status_color, line=dict(color='white', width=1)),
                customdata=raw_data + [raw_data[0]],
                hovertemplate='<b>%{theta}</b><br>' +
                              'Status: <b>%{r:.0f}%</b><br>' +
                              'Value: <b>%{customdata:.2f}</b><extra></extra>',
                showlegend=True
            ))
    
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        showticklabels=False,
                        # gridcolor='rgba(255, 255, 255, 0.05)',
                        gridcolor='rgba(148, 163, 184, 0.2)', 
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color='#94a3b8', family="Plus Jakarta Sans"),
                        gridcolor='rgba(148, 163, 184, 0.2)',
                        linecolor='rgba(255, 255, 255, 0.1)'
                    ),
                    bgcolor='rgba(0,0,0,0)'
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(color="#f8fafc", family="Outfit")
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc', family="Outfit"),
                margin=dict(l=40, r=40, t=20, b=20),
                height=350,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
