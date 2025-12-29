import streamlit as st
import pandas as pd
from back.src.heatmap import page_heatmap, radar_chart
from back.query.queries import get_data_water

def render_heatmap_page():
     st.markdown("## 🔥 Environmental Heatmap")
        
     # Load data (Cached)
     df = get_data_water()
     
     # Layout Containers
     c_overview = st.container()
     st.divider()
     c_map = st.container()
     st.divider()
     c_filter = st.container()

     # --- Filter Logic (Bottom) ---
     filtered_df = df # Default
     if not df.empty and 'latest_timestamp' in df.columns:
         valid_dates = pd.to_datetime(df['latest_timestamp'], errors='coerce').dropna()
         if not valid_dates.empty:
             df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'])
             min_date = valid_dates.min().date()
             max_date = valid_dates.max().date()
             if min_date == max_date:
                 min_date = min_date - pd.Timedelta(days=1)
             
             with c_filter:
                 st.markdown("### 🗓️ Filter Tanggal")
                 date_range = st.slider(
                     "Geser untuk memfilter data:",
                     min_value=min_date,
                     max_value=max_date,
                     value=(min_date, max_date),
                     format="DD/MM/YY"
                 )
                 
                 # Apply Filter
                 mask = (df['latest_timestamp'].dt.date >= date_range[0]) & (df['latest_timestamp'].dt.date <= date_range[1])
                 filtered_df = df[mask]
     
     # --- Area Overview (Top) ---
     with c_overview:
         st.markdown("### 🕸️ Area Overview")
         radar_chart(filtered_df)

     # --- Maps (Middle) ---
     with c_map:
         tab_main_sel = st.radio("Select Category", ["Water Quality", "Oceanographic"], horizontal=True)
         
         if tab_main_sel == "Water Quality":
              col1, col2 = st.columns(2)
              with col1: 
                  st.write("**Salinity**")
                  page_heatmap(filtered_df, "salinitas")
              with col2:
                  st.write("**Turbidity**")
                  page_heatmap(filtered_df, "turbidity")
              
              st.markdown("**Oxygen**", help="Dissolved Oxygen levels")
              page_heatmap(filtered_df, "oxygen")
              
         else:
              col1, col2 = st.columns(2)
              with col1:
                  st.write("**Current**")
                  page_heatmap(filtered_df, "current")
              with col2:
                  st.write("**Tide**")
                  page_heatmap(filtered_df, "tide")
             
              st.markdown("**Density**", help="Seawater Density")
              page_heatmap(filtered_df, "density")
