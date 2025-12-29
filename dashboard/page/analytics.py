import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from back.query.queries import get_financial_metrics, get_revenue_analysis, get_order_stats

def calculate_forecast(df):
    """Simple Moving Average Forecast for next 3 months"""
    if df.empty or 'revenue' not in df.columns:
        return pd.DataFrame()
        
    df = df.sort_values('month')
    last_date = df['month'].iloc[-1]
    # Explicit float conversion
    last_val = float(df['revenue'].iloc[-1])
    
    growth_rate = 0.05 
    
    future_dates = [last_date + pd.DateOffset(months=i) for i in range(1, 4)]
    # Ensure float list
    future_vals = [float(last_val * ((1 + growth_rate) ** i)) for i in range(1, 4)]
    
    return pd.DataFrame({'month': future_dates, 'revenue': future_vals, 'type': 'Forecast'})

def render_analytics_page():
    st.markdown("## 📈 Advanced Analytics Hub")
    
    # --- Load Data ---
    fin = get_financial_metrics()
    rev_df = get_revenue_analysis() 
    orders = get_order_stats()
    
    # --- Top KPIs (Explicit Casting) ---
    c1, c2, c3, c4 = st.columns(4)
    
    total_revenue = float(fin.get('total_revenue', 0))
    delta_revenue = float(fin.get('delta_revenue', 0.0))
    c1.metric("Total Revenue", f"IDR {total_revenue:,.0f}", f"{delta_revenue:.1f}%")
    
    total_orders = int(orders.get('total_orders', 0))
    failed_orders = int(orders.get('failed', 0))
    completed_orders = int(orders.get('completed', 0))
    
    fail_rate = 0.0
    if total_orders > 0:
        fail_rate = (failed_orders / total_orders) * 100.0
        
    c2.metric("Total Orders", total_orders, f"Fail Rate: {fail_rate:.1f}%")
    c3.metric("Completed Missions", completed_orders, "100% Success")
    c4.metric("Active Clients", "18", "+2 New")

    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Financial Performance", "🚢 Fleet Utilization", "📑 Reports"])
    
    with tab1:
        st.subheader("Revenue Forecast (Q1 2026)")
        
        if not rev_df.empty:
            rev_df['type'] = 'Actual'
            # Ensure native types in DF
            rev_df['revenue'] = rev_df['revenue'].astype(float)
            
            forecast_df = calculate_forecast(rev_df)
            combined_df = pd.concat([rev_df, forecast_df])
            
            fig = px.area(
                combined_df, x='month', y='revenue', color='type',
                template="plotly_dark",
                color_discrete_map={'Actual': '#38bdf8', 'Forecast': '#a855f7'}
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Outfit", color="#8b9bb4"),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="rgba(148, 163, 184, 0.1)"),
                legend=dict(orientation="h", y=1.1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Insufficient data for forecasting.")

        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.markdown("#### 💰 Revenue Composition")
            comp_df = pd.DataFrame([
                {'Service': 'Vessel Charter', 'Value': 65.0},
                {'Service': 'Logistics', 'Value': 25.0},
                {'Service': 'Consulting', 'Value': 10.0},
            ])
            fig_pie = px.pie(comp_df, values='Value', names='Service', hole=0.6, color_discrete_sequence=px.colors.sequential.Teal)
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c_right:
             st.markdown("#### 📉 Monthly Growth Rate")
             if not rev_df.empty and len(rev_df) > 1:
                rev_df['growth'] = rev_df['revenue'].pct_change() * 100.0
                fig_bar = px.bar(rev_df.dropna(), x='month', y='growth', color='growth', color_continuous_scale='RdBu')
                fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_bar, use_container_width=True)


    with tab2:
        st.subheader("Fleet Activity Heatmap")
        st.caption("Operational Hours per Day (Mock Data)")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        vessels = [f"Vessel-{i}" for i in range(1, 11)]
        # Use lists directly instead of numpy
        z_data = [
            [12, 14, 10, 8, 20, 22, 5],
            [10, 12, 11, 9, 18, 20, 4],
            [5, 5, 20, 22, 24, 0, 0],
            [18, 18, 18, 18, 18, 10, 2],
            [8, 8, 8, 8, 8, 5, 5],
            [22, 24, 20, 15, 10, 5, 0],
            [0, 0, 5, 10, 15, 20, 22],
            [12, 12, 12, 12, 12, 12, 12],
            [14, 16, 18, 20, 22, 24, 2],
            [9, 9, 9, 9, 9, 2, 2]
        ]
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=days,
            y=vessels,
            colorscale='Viridis'
        ))
        fig.update_layout(
             paper_bgcolor='rgba(0,0,0,0)',
             plot_bgcolor='rgba(0,0,0,0)',
             font=dict(color="#8b9bb4"),
             height=500
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        st.subheader("Download Operational Reports")
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("📄 **Monthly Financial Report (PDF)**")
            st.button("Download PDF", key="btn_pdf")
            
        with c2:
            st.info("📊 **Raw Transaction Data (CSV)**")
            if not rev_df.empty:
                csv = rev_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name='revenue_data.csv',
                    mime='text/csv',
                )
