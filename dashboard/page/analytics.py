import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from back.query.queries import (
    get_financial_metrics, get_revenue_analysis, get_order_stats,
    get_vessel_utilization_stats, get_revenue_cycle_metrics,
    get_environmental_anomalies, get_logistics_performance
)
from back.src.forecast import calculate_advanced_forecast
from back.src.utils import apply_chart_style

def render_analytics_page():
    st.markdown("## 📈 Advanced Analytics Hub")
    
    fin = get_financial_metrics()
    rev_df = get_revenue_analysis() 
    orders = get_order_stats()
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Financial Performance", "🚢 Fleet Intelligence", "🌱 Environmental", "📑 Reports"])
    
    with tab1:
        st.subheader("Revenue Forecast")
        
        if not rev_df.empty:
            rev_df['type'] = 'Actual'
            rev_df['lower_bound'] = rev_df['revenue']
            rev_df['upper_bound'] = rev_df['revenue']
            rev_df['revenue'] = rev_df['revenue'].astype(float)
            
            forecast_df = calculate_advanced_forecast(rev_df, months=6)
            
            if not forecast_df.empty:
                combined_df = pd.concat([rev_df, forecast_df])
                
                fig = go.Figure()
                
                actual = combined_df[combined_df['type'] == 'Actual']
                fig.add_trace(go.Scatter(
                    x=actual['month'], y=actual['revenue'],
                    mode='lines+markers', name='Actual Revenue',
                    line=dict(color='#38bdf8', width=3)
                ))
                
                forecast = combined_df[combined_df['type'] == 'Forecast']
                fig.add_trace(go.Scatter(
                    x=forecast['month'], y=forecast['revenue'],
                    mode='lines+markers', name='Projected (Trend)',
                    line=dict(color='#a855f7', width=3, dash='dash')
                ))
                
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

                apply_chart_style(fig)
                fig.update_layout(yaxis_title="Revenue (IDR)", xaxis_title="Month")
                
                last_actual_date = actual['month'].iloc[-1].timestamp() * 1000
                fig.add_vline(x=last_actual_date, line_dash="dot", line_color="white", annotation_text="Today")
                
                st.plotly_chart(fig, use_container_width=True)
                model_name = forecast_df['model_name'].iloc[0]
                st.caption(f"ℹ️ **Methodology**: Automatically selected **{model_name} Model** based on lowest error rate (RMSE). Shaded area represents uncertainty.")
            else:
                st.warning("Not enough data points to generate a reliable regression forecast.")
        else:
            st.info("Insufficient data for forecasting.")

        st.markdown("---")
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            st.markdown("#### 💰 Revenue Composition")
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
                
        with col_rev2:
            st.markdown("#### ⏳ Order-to-Cash Cycle")
            cycle_df = get_revenue_cycle_metrics()
            if not cycle_df.empty:
                fig_cycle = go.Figure()
                fig_cycle.add_trace(go.Bar(
                    x=cycle_df['month'], y=cycle_df['avg_days_to_cash'],
                    name='Avg Days to Cash', marker_color='#f59e0b'
                ))
                fig_cycle.update_layout(yaxis_title="Days")
                apply_chart_style(fig_cycle)
                st.plotly_chart(fig_cycle, use_container_width=True)
                st.caption("Average time from Order Date to Payment Date. Lower is better.")
            else:
                st.info("No cycle data available.")

    with tab2:
        st.subheader("Fleet Activity Heatmap")
        st.caption("Active Operational Hours (Last 7 Days)")
        
        activity_df = get_fleet_daily_activity()
        
        if not activity_df.empty:
            heatmap_data = activity_df.pivot(index="code_vessel", columns="day_name", values="active_hours").fillna(0)
            
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
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No vessel activity data found for the last 7 days.")
            
        st.markdown("---")
        
        c_fleet1, c_fleet2 = st.columns(2)
        
        with c_fleet1:
            st.subheader("🚜 Asset Utilization")
            util_df = get_vessel_utilization_stats()
            if not util_df.empty:
                avg_util = util_df['utilization_rate'].mean()
                fig_util = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = avg_util,
                    title = {'text': "Avg Fleet Utilization"},
                    gauge = {'axis': {'range': [0, 100]},
                             'bar': {'color': "#10b981"},
                             'steps' : [
                                 {'range': [0, 50], 'color': "#374151"},
                                 {'range': [50, 80], 'color': "#4b5563"}],
                             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}
                ))
                apply_chart_style(fig_util)
                fig_util.update_layout(height=300)
                st.plotly_chart(fig_util, use_container_width=True)
                
                with st.expander("Usage Details by Vessel"):
                    st.dataframe(util_df[['vessel_name', 'total_hours', 'productive_hours', 'utilization_rate']], use_container_width=True)
            else:
                st.info("No utilization data available.")
                
        with c_fleet2:
            st.subheader("🚚 Logistics Performance")
            log_df = get_logistics_performance()
            if not log_df.empty:
               try:
                   st.dataframe(
                       log_df.style.background_gradient(subset=['avg_delay_hours'], cmap='RdYlGn_r'),
                       use_container_width=True
                   )
               except ImportError:
                   st.dataframe(log_df, use_container_width=True)
               except Exception as e:
                   st.dataframe(log_df, use_container_width=True)
               
               st.caption("Negative delay means early delivery.")
            else:
                st.info("No delivery data available.")

    with tab3:
        st.subheader("🌊 Environmental Anomalies Detection")
        st.markdown("**AI-Driven Insight**: Detecting deviations in water quality parameters (Salinity & Turbidity) > 2 Standard Deviations.")
        
        anom_df = get_environmental_anomalies()
        
        if not anom_df.empty:
            st.error(f"⚠️ Detected {len(anom_df)} anomalous readings in the last 7 days.")
            
            fig_anom = px.scatter(anom_df, x='created_at', y='salinitas', color='sal_z_score',
                                  size='tur_z_score', hover_data=['id_buoy', 'turbidity'],
                                  title="Anomaly Severity (Color=Salinity Z, Size=Turbidity Z)",
                                  color_continuous_scale='Reds')
            apply_chart_style(fig_anom)
            st.plotly_chart(fig_anom, use_container_width=True)
            
            st.dataframe(anom_df, use_container_width=True)
        else:
            st.success("✅ No significant environmental anomalies detected in the last 7 days.")

    with tab4:
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
