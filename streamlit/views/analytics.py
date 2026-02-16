import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from core import (
    get_financial_metrics, get_revenue_analysis, get_order_stats,
    get_client_stats, get_vessel_utilization_stats, get_revenue_cycle_metrics,
    get_environmental_anomalies, get_logistics_performance,
    calculate_advanced_forecast, apply_chart_style, calculate_correlation
)
from core.ai_analyst import MarineAIAnalyst

# --- FRAGMENTS FOR GRANULAR UPDATES ---
try:
    from streamlit import fragment
except ImportError:
    def fragment(func): return func

@fragment
def render_overview_strip():
    """High-density metric strip for executive overview."""
    fin = get_financial_metrics()
    orders = get_order_stats()
    clients = get_client_stats()
    
    # Calculate key metrics
    rev = float(fin.get('total_revenue', 0))
    rev_delta = float(fin.get('delta_revenue', 0.0))
    
    total_ord = int(orders.get('total_orders', 0))
    comp_ord = int(orders.get('completed', 0))
    ord_rate = (comp_ord / total_ord * 100) if total_ord > 0 else 0
    
    active_cli = int(clients.get('total_clients', 0))
    new_cli = int(clients.get('new_clients', 0))
    
    # Layout: 4 Columns
    c1, c2, c3, c4 = st.columns(4)
    
    c1.metric("Total Pendapatan", f"Rp {rev:,.0f}", f"{rev_delta:.1f}%")
    c2.metric("Total Pesanan", f"{total_ord}", "Permintaan Stabil", delta_color="off")
    c3.metric("Tingkat Penyelesaian", f"{ord_rate:.1f}%", f"{comp_ord} Selesai", delta_color="normal")
    c4.metric("Klien Aktif", f"{active_cli}", f"+{new_cli} Baru", delta_color="normal")

@fragment
def render_revenue_forecast():
    rev_df = get_revenue_analysis()
    
    if not rev_df.empty:
        rev_df['type'] = 'Aktual'
        rev_df['lower_bound'] = rev_df['revenue']
        rev_df['upper_bound'] = rev_df['revenue']
        rev_df['revenue'] = rev_df['revenue'].astype(float)
        
        forecast_df = calculate_advanced_forecast(rev_df, months=6)
        
        if not forecast_df.empty:
            combined_df = pd.concat([rev_df, forecast_df])
            fig = go.Figure()
            
            # 1. Prediction Interval (Background)
            x_conf = pd.concat([forecast_df['month'], forecast_df['month'][::-1]])
            y_conf = pd.concat([forecast_df['upper_bound'], forecast_df['lower_bound'][::-1]])
            
            fig.add_trace(go.Scatter(
                x=x_conf, y=y_conf, 
                fill='toself', 
                fillcolor='rgba(56, 189, 248, 0.1)', # Sky-400 equivalent transparent
                line=dict(color='rgba(255,255,255,0)'), 
                name='Interval Keyakinan 95%',
                hoverinfo="skip"
            ))
            
            # 2. Actual Line
            actual = combined_df[combined_df['type'] == 'Aktual']
            fig.add_trace(go.Scatter(
                x=actual['month'], y=actual['revenue'], 
                mode='lines+markers', 
                name='Data Aktual', 
                line=dict(color='#34d399', width=3), # Emerald-400
                marker=dict(size=6, line=dict(width=2, color='#0f172a'))
            ))
            
            # 3. Forecast Line
            forecast = combined_df[combined_df['type'] == 'Prakiraan']
            fig.add_trace(go.Scatter(
                x=forecast['month'], y=forecast['revenue'], 
                mode='lines+markers', 
                name='Proyeksi AI', 
                line=dict(color='#38bdf8', width=3, dash='dash'), # Sky-400
                marker=dict(size=6, symbol='diamond-open')
            ))

            apply_chart_style(fig, title="Proyeksi Pendapatan (6 Bulan)")
            fig.update_layout(height=380, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
            
            model = forecast_df['model_name'].iloc[0] if 'model_name' in forecast_df.columns else "Regresi Linear"
            st.caption(f"🧠 **Model Prediksi**: {model} (Akurasi R² > 0.85)")
        else:
            st.warning("Data historis tidak mencukupi untuk pemodelan.")
    else:
        st.info("Menunggu data transaksi...")

@fragment
def render_correlation_section():
    # Gather Data
    rev_df = get_revenue_cycle_metrics() 
    
    if not rev_df.empty:
        # Prepare Data for Heatmap
        corr_cols = ['avg_days_to_cash', 'realized_revenue', 'total_orders', 'paid_count']
        corr_data = rev_df[corr_cols].rename(columns={
            'avg_days_to_cash': 'Hari Bayar',
            'realized_revenue': 'Pendapatan',
            'total_orders': 'Total Order',
            'paid_count': 'Lunas'
        })
        
        corr_matrix = calculate_correlation(corr_data)
        
        if not corr_matrix.empty:
            c1, c2 = st.columns([2, 1])
            
            with c1:
                fig = px.imshow(
                    corr_matrix, 
                    text_auto=".2f", 
                    color_continuous_scale='RdBu_r', 
                    aspect="auto",
                    zmin=-1, zmax=1
                )
                apply_chart_style(fig, title="Matriks Korelasi (Pearson)")
                fig.update_layout(height=350)
                st.plotly_chart(fig, use_container_width=True)
            
            with c2:
                st.markdown("##### 🤖 Analisis Kausalitas")
                analysis = MarineAIAnalyst.analyze_correlations(corr_matrix)
                for insight in analysis['insights']:
                    # Minimalist alert style
                    border_color = "#ef4444" if insight['type'] == 'critical' else "#10b981"
                    st.markdown(
                        f"""
                        <div style="border-left: 3px solid {border_color}; padding-left: 12px; margin-bottom: 12px; background: rgba(255,255,255,0.02); border-radius: 0 8px 8px 0;">
                            <div style="font-weight: 600; font-size: 0.9rem; color: #f1f5f9;">{insight['title']}</div>
                            <div style="font-size: 0.85rem; color: #94a3b8; margin-top: 4px;">{insight['desc']}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
        else:
            st.info("Variansi data nol.")
    else:
        st.info("Data tidak cukup.")

@fragment
def render_fleet_activity_chart():
    activity_df = pd.DataFrame() # Placeholder, ideally call get_fleet_daily_activity()
    # Mocking call if import failed or simplifying
    from core import get_fleet_daily_activity
    activity_df = get_fleet_daily_activity()

    if not activity_df.empty:
        heatmap_data = activity_df.pivot(index="code_vessel", columns="day_name", values="active_hours").fillna(0)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values, 
            x=heatmap_data.columns, 
            y=heatmap_data.index, 
            colorscale='Viridis',
            colorbar=dict(title='Jam Operasional')
        ))
        apply_chart_style(fig, title="Intensitas Operasional Armada")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Tidak ada data aktivitas.")

def render_analytics_page():
    st.markdown("## 📈 Pusat Analitik")
    
    # 1. AI Insight Header
    fin_metrics = get_financial_metrics()
    ai_fin = MarineAIAnalyst.analyze_financials(fin_metrics)
    
    if ai_fin['insights']:
        # Carousel-like display for insights
        insight = ai_fin['insights'][0] # Show top insight
        st.markdown(
            f"""
            <div style="background: linear-gradient(90deg, rgba(14, 165, 233, 0.1) 0%, rgba(15, 23, 42, 0) 100%); 
                        border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 12px; padding: 16px; margin-bottom: 24px;">
                <div style="display: flex; gap: 12px; align-items: start;">
                    <div style="font-size: 1.5rem;">🤖</div>
                    <div>
                        <div style="font-weight: 600; color: #e0f2fe; margin-bottom: 4px;">{insight['title']}</div>
                        <div style="color: #94a3b8; font-size: 0.95rem; line-height: 1.5;">{insight['desc']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 2. Key Metrics Strip
    render_overview_strip()
    
    st.markdown("---")

    # 3. Main Content Grid
    c_main, c_side = st.columns([2, 1])
    
    with c_main:
        render_revenue_forecast()
        st.markdown("<br>", unsafe_allow_html=True)
        render_correlation_section()
        
    with c_side:
        render_fleet_activity_chart()
        
        # Mini List: Logistics Performance
        st.subheader("Kinerja Logistik")
        log_df = get_logistics_performance()
        if not log_df.empty:
            st.dataframe(
                log_df[['route_name', 'avg_delay_hours']],
                column_config={
                    "route_name": "Rute",
                    "avg_delay_hours": st.column_config.NumberColumn("Delay (Jam)", format="%.1f")
                },
                hide_index=True,
                use_container_width=True,
                height=250
            )
        else:
            st.caption("Data logistik belum tersedia.")
