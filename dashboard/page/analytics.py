import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from back.query.queries import get_financial_metrics, get_revenue_analysis, get_order_stats
from back.src.forecast import calculate_advanced_forecast
from back.src.utils import apply_chart_style



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
        st.subheader("Revenue Forecast")
        
        if not rev_df.empty:
            rev_df['type'] = 'Actual'
            rev_df['lower_bound'] = rev_df['revenue']
            rev_df['upper_bound'] = rev_df['revenue']
            # Ensure native types in DF
            rev_df['revenue'] = rev_df['revenue'].astype(float)
            
            # Use new advanced forecast
            forecast_df = calculate_advanced_forecast(rev_df, months=6)
            
            if not forecast_df.empty:
                combined_df = pd.concat([rev_df, forecast_df])
                
                # Main Line Chart
                fig = go.Figure()
                
                # Actual Data
                actual = combined_df[combined_df['type'] == 'Actual']
                fig.add_trace(go.Scatter(
                    x=actual['month'], y=actual['revenue'],
                    mode='lines+markers', name='Actual Revenue',
                    line=dict(color='#38bdf8', width=3)
                ))
                
                # Forecast Data
                forecast = combined_df[combined_df['type'] == 'Forecast']
                fig.add_trace(go.Scatter(
                    x=forecast['month'], y=forecast['revenue'],
                    mode='lines+markers', name='Projected (Trend)',
                    line=dict(color='#a855f7', width=3, dash='dash')
                ))
                
                # Confidence Interval (Shaded Area)
                # Concatenate X coordinates forward and backward for the closed shape
                x_conf = pd.concat([forecast['month'], forecast['month'][::-1]])
                y_conf = pd.concat([forecast['upper_bound'], forecast['lower_bound'][::-1]])
                
                fig.add_trace(go.Scatter(
                    x=x_conf,
                    y=y_conf,
                    fill='toself',
                    fillcolor='rgba(168, 85, 247, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% Confidence Interval',
                    showlegend=True
                ))

                # Standard Style
                apply_chart_style(fig)
                fig.update_layout(yaxis_title="Revenue (IDR)", xaxis_title="Month")
                
                # Vertical line for "Today"
                last_actual_date = actual['month'].iloc[-1].timestamp() * 1000
                fig.add_vline(x=last_actual_date, line_dash="dot", line_color="white", annotation_text="Today")
                
                st.plotly_chart(fig, use_container_width=True)
                model_name = forecast_df['model_name'].iloc[0]
                st.caption(f"ℹ️ **Methodology**: Automatically selected **{model_name} Model** based on lowest error rate (RMSE). Shaded area represents uncertainty.")
            else:
                st.warning("Not enough data points to generate a reliable regression forecast.")
        else:
            st.info("Insufficient data for forecasting.")

        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.markdown("#### 💰 Revenue Composition")
            # --- REAL DATA: Revenue by Service (Industry) ---
            from back.query.queries import get_revenue_by_service, get_fleet_daily_activity
            
            comp_df = get_revenue_by_service()
            if not comp_df.empty:
                fig_pie = px.pie(comp_df, values='Value', names='Service', hole=0.6, 
                                 title="Revenue by Industry",
                                 color_discrete_sequence=px.colors.sequential.Teal)
                apply_chart_style(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No revenue data to display.")
            
        with c_right:
             st.markdown("#### 📉 Monthly Growth Rate (%)")
             if not rev_df.empty and len(rev_df) > 1:
                # Calculate percentage growth
                rev_df = rev_df.sort_values('month', ascending=True)
                rev_df['growth'] = rev_df['revenue'].pct_change() * 100.0
                
                # Drop the first NaN
                chart_data = rev_df.dropna(subset=['growth'])
                
                fig_line = go.Figure()
                fig_line.add_trace(go.Scatter(
                    x=chart_data['month'],
                    y=chart_data['growth'],
                    mode='lines+markers',
                    name='Growth Rate',
                    line=dict(color='#38bdf8', width=3),
                    marker=dict(size=8, color='#38bdf8')
                ))
                
                # Add a zero line reference
                fig_line.add_hline(y=0, line_dash="dot", line_color="white", opacity=0.5)

                apply_chart_style(fig_line)
                fig_line.update_layout(yaxis_title="Growth (%)")
                st.plotly_chart(fig_line, use_container_width=True)


    with tab2:
        st.subheader("Fleet Activity Heatmap")
        st.caption("Active Operational Hours (Last 7 Days)")
        
        # --- REAL DATA: Fleet Activity ---
        activity_df = get_fleet_daily_activity()
        
        if not activity_df.empty:
            # Pivot data for heatmap: Index=Vessel, Columns=DayName, Values=Hours
            # We want day order Mon->Sun. The query returns day_num.
            
            heatmap_data = activity_df.pivot(index="code_vessel", columns="day_name", values="active_hours").fillna(0)
            
            # Sort columns loosely by weekday order if possible (naive sort might be alphabetical)
            # A better way is to rely on simple sorting or just display as is.
            days_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            existing_days = [d for d in days_order if d in heatmap_data.columns]
            heatmap_data = heatmap_data[existing_days]
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                colorbar=dict(title='Hours Active')
            ))
            apply_chart_style(fig)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No vessel activity data found for the last 7 days.")
        
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
