import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dashboard.core import (
    get_financial_metrics, get_revenue_analysis, get_order_stats,
    get_vessel_utilization_stats, get_revenue_cycle_metrics,
    get_environmental_anomalies, get_logistics_performance,
    calculate_advanced_forecast, apply_chart_style
)

def render_analytics_page():
    st.markdown("## 📈 Pusat Analitik Lanjutan")
    
    fin = get_financial_metrics()
    rev_df = get_revenue_analysis() 
    orders = get_order_stats()
    
    c1, c2, c3, c4 = st.columns(4)
    
    total_revenue = float(fin.get('total_revenue', 0))
    delta_revenue = float(fin.get('delta_revenue', 0.0))
    c1.metric("Total Pendapatan", f"Rp {total_revenue:,.0f}", f"{delta_revenue:.1f}%")
    
    total_orders = int(orders.get('total_orders', 0))
    failed_orders = int(orders.get('failed', 0))
    completed_orders = int(orders.get('completed', 0))
    
    fail_rate = 0.0
    if total_orders > 0:
        fail_rate = (failed_orders / total_orders) * 100.0
        
    c2.metric("Total Pesanan", total_orders, f"Gagal: {fail_rate:.1f}%")
    c3.metric("Misi Selesai", completed_orders, "100% Sukses")
    c4.metric("Klien Aktif", "18", "+2 Baru")

    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Kinerja Keuangan", "🚢 Intelijen Armada", "🌱 Lingkungan", "📑 Laporan"])
    
    with tab1:
        st.subheader("Prakiraan Pendapatan")
        
        if not rev_df.empty:
            rev_df['type'] = 'Aktual'
            rev_df['lower_bound'] = rev_df['revenue']
            rev_df['upper_bound'] = rev_df['revenue']
            rev_df['revenue'] = rev_df['revenue'].astype(float)
            
            forecast_df = calculate_advanced_forecast(rev_df, months=6)
            
            if not forecast_df.empty:
                combined_df = pd.concat([rev_df, forecast_df])
                
                fig = go.Figure()
                
                actual = combined_df[combined_df['type'] == 'Aktual']
                fig.add_trace(go.Scatter(
                    x=actual['month'], y=actual['revenue'],
                    mode='lines+markers', name='Pendapatan Aktual',
                    line=dict(color='#38bdf8', width=3)
                ))
                
                forecast = combined_df[combined_df['type'] == 'Prakiraan']
                fig.add_trace(go.Scatter(
                    x=forecast['month'], y=forecast['revenue'],
                    mode='lines+markers', name='Proyeksi (Tren)',
                    line=dict(color='#a855f7', width=3, dash='dash')
                ))
                
                x_conf = pd.concat([forecast['month'], forecast['month'][::-1]])
                y_conf = pd.concat([forecast['upper_bound'], forecast['lower_bound'][::-1]])
                
                fig.add_trace(go.Scatter(
                    x=x_conf, y=y_conf, fill='toself',
                    fillcolor='rgba(168, 85, 247, 0.2)', line=dict(color='rgba(255,255,255,0)'),
                    name='Interval Kepercayaan 95%', showlegend=True
                ))

                apply_chart_style(fig)
                fig.update_layout(yaxis_title="Pendapatan (IDR)", xaxis_title="Bulan")
                st.plotly_chart(fig, use_container_width=True)
                
                model_name = forecast_df['model_name'].iloc[0]
                st.caption(f"ℹ️ **Metodologi**: Model **{model_name}** dipilih secara otomatis berdasarkan tingkat kesalahan terendah (RMSE).")
            else:
                st.warning("Data tidak cukup untuk membuat prakiraan.")
        else:
            st.info("Data tidak memadai untuk prakiraan.")

        st.markdown("---")
        
        col_rev1, col_rev2 = st.columns(2)
        with col_rev1:
            st.markdown("#### 💰 Komposisi Pendapatan")
            from dashboard.core import get_revenue_by_service, get_fleet_daily_activity
            
            comp_df = get_revenue_by_service()
            if not comp_df.empty:
                fig_pie = px.pie(comp_df, values='Nilai', names='Layanan', hole=0.6, 
                                 title="Pendapatan per Industri",
                                 color_discrete_sequence=px.colors.sequential.Teal)
                apply_chart_style(fig_pie)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Tidak ada data pendapatan.")
                
        with col_rev2:
            st.markdown("#### ⏳ Siklus Pesanan-ke-Kas")
            cycle_df = get_revenue_cycle_metrics()
            if not cycle_df.empty:
                fig_cycle = go.Figure()
                fig_cycle.add_trace(go.Bar(
                    x=cycle_df['month'], y=cycle_df['avg_days_to_cash'],
                    name='Rata-rata Hari Cair', marker_color='#f59e0b'
                ))
                fig_cycle.update_layout(yaxis_title="Hari")
                apply_chart_style(fig_cycle)
                st.plotly_chart(fig_cycle, use_container_width=True)
                st.caption("Rata-rata waktu dari Tanggal Pesanan ke Tanggal Pembayaran. Lebih rendah lebih baik.")
            else:
                st.info("Tidak ada data siklus.")

    with tab2:
        st.subheader("Peta Panas Aktivitas Armada")
        st.caption("Jam Operasional Aktif (7 Hari Terakhir)")
        
        activity_df = get_fleet_daily_activity()
        
        if not activity_df.empty:
            heatmap_data = activity_df.pivot(index="code_vessel", columns="day_name", values="active_hours").fillna(0)
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values, x=heatmap_data.columns, y=heatmap_data.index,
                colorscale='Viridis', colorbar=dict(title='Jam Aktif')
            ))
            apply_chart_style(fig)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Tidak ada data aktivitas armada.")
            
        st.markdown("---")
        
        c_fleet1, c_fleet2 = st.columns(2)
        with c_fleet1:
            st.subheader("🚜 Utilisasi Aset")
            util_df = get_vessel_utilization_stats()
            if not util_df.empty:
                avg_util = util_df['utilization_rate'].mean()
                fig_util = go.Figure(go.Indicator(
                    mode = "gauge+number", value = avg_util,
                    title = {'text': "Rata-rata Utilisasi Armada"},
                    gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "#10b981"},
                             'steps' : [{'range': [0, 50], 'color': "#374151"}, {'range': [50, 80], 'color': "#4b5563"}],
                             'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 90}}
                ))
                apply_chart_style(fig_util)
                fig_util.update_layout(height=300)
                st.plotly_chart(fig_util, use_container_width=True)
                with st.expander("Detail Penggunaan per Kapal"):
                    st.dataframe(util_df[['vessel_name', 'total_hours', 'productive_hours', 'utilization_rate']], use_container_width=True)
            else: st.info("Data utilisasi tidak tersedia.")
                
        with c_fleet2:
            st.subheader("🚚 Kinerja Logistik")
            log_df = get_logistics_performance()
            if not log_df.empty:
               st.dataframe(log_df, use_container_width=True)
               st.caption("Keterlambatan negatif berarti pengiriman lebih awal.")
            else: st.info("Data pengiriman tidak tersedia.")

    with tab3:
        st.subheader("🌊 Deteksi Anomali Lingkungan")
        st.markdown("**Wawasan AI**: Mendeteksi penyimpangan parameter kualitas air (Salinitas & Kekeruhan) > 2 Standar Deviasi.")
        anom_df = get_environmental_anomalies()
        
        if not anom_df.empty:
            st.error(f"⚠️ Terdeteksi {len(anom_df)} pembacaan anomali dalam 7 hari terakhir.")
            fig_anom = px.scatter(anom_df, x='created_at', y='salinitas', color='sal_z_score',
                                  size='tur_z_score', hover_data=['id_buoy', 'turbidity'],
                                  title="Keparahan Anomali", color_continuous_scale='Reds')
            apply_chart_style(fig_anom)
            st.plotly_chart(fig_anom, use_container_width=True)
            st.dataframe(anom_df, use_container_width=True)
        else:
            st.success("✅ Tidak ada anomali lingkungan signifikan.")

    with tab4:
        st.subheader("Unduh Laporan Operasional")
        c1, c2 = st.columns(2)
        with c1:
            st.info("📄 **Laporan Keuangan Bulanan (PDF)**")
            st.button("Unduh PDF", key="btn_pdf")
        with c2:
            st.info("📊 **Data Transaksi Mentah (CSV)**")
            if not rev_df.empty:
                csv = rev_df.to_csv(index=False).encode('utf-8')
                st.download_button(label="Unduh CSV", data=csv, file_name='revenue_data.csv', mime='text/csv')
