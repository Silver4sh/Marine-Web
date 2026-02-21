import streamlit as st
import pandas as pd
import altair as alt
from core import get_data_water, page_heatmap, load_html
from core.database import get_buoy_fleet, get_buoy_history
from core.ai_analyst import MarineAIAnalyst


def render_chart(df, x_col, y_col, color_col, title):
    if df.empty or y_col not in df.columns:
        st.info("Tidak ada data untuk ditampilkan.")
        return

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X(x_col, title="Waktu"),
        y=alt.Y(y_col, title=""),
        color=alt.Color(color_col, legend=None),
        tooltip=[x_col, y_col, color_col]
    ).properties(height=300)

    if title:
        chart = chart.properties(title=title)

    st.altair_chart(chart.interactive(), use_container_width=True)


def render_sparkline(df, y_col, title, color="#0ea5e9"):
    if df.empty or y_col not in df.columns:
        return

    chart = alt.Chart(df).mark_area(
        line={'color': color},
        color=alt.Gradient(
            gradient='linear',
            stops=[alt.GradientStop(color=color, offset=0),
                   alt.GradientStop(color='white', offset=1)],
            x1=1, x2=1, y1=1, y2=0
        )
    ).encode(
        x=alt.X('created_at', axis=alt.Axis(labels=False, grid=False, title="")),
        y=alt.Y(y_col, axis=alt.Axis(labels=True, grid=True, title="")),
        tooltip=['created_at', y_col]
    ).properties(title=title, height=150)
    st.altair_chart(chart, use_container_width=True)


def _section_header(icon: str, title: str, subtitle: str = ""):
    sub = f'<div style="font-size:0.78rem; color:#8ba3c0; margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:12px; margin-top:6px;">
            <span style="font-size:1.2rem;">{icon}</span>
            <div>
                <div style="font-family:'Outfit',sans-serif; font-size:1rem; font-weight:800; color:#f0f6ff; letter-spacing:-0.01em;">{title}</div>
                {sub}
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_environ_heatmap():
    _section_header("🔥", "Enviro Heatmap", "Distribusi spasial parameter lingkungan")
    df = get_data_water()

    # AI Analysis for Environment — with correct severity display
    anomaly_df = df[df['salinitas'] > 40] if not df.empty and 'salinitas' in df.columns else pd.DataFrame()
    ai_env = MarineAIAnalyst.analyze_environment(anomaly_df)

    with st.expander("🤖 AI Eco-Watch", expanded=True):
        for insight in ai_env['insights']:
            itype = insight.get('type', 'info')
            if itype == 'critical':
                st.error(f"**{insight['title']}**\n\n{insight['desc']}")
            elif itype == 'warning':
                st.warning(f"**{insight['title']}**\n\n{insight['desc']}")
            elif itype == 'positive':
                st.success(f"**{insight['title']}**\n\n{insight['desc']}")
            else:
                st.info(f"**{insight['title']}**\n\n{insight['desc']}")

    if not df.empty and 'latest_timestamp' in df.columns:
        df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'])
        max_date = df['latest_timestamp'].max()
        start_date = max_date - pd.Timedelta(days=7)
        df = df[df['latest_timestamp'] >= start_date]

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)
    c1, c2 = st.columns(2)

    if cat == "Kualitas Air":
        with c1:
            st.caption("🧂 Salinitas")
            page_heatmap(df, "salinitas")
        with c2:
            st.caption("🌫️ Kekeruhan")
            page_heatmap(df, "turbidity")
        st.caption("💨 Oksigen")
        page_heatmap(df, "oxygen")
    else:
        chart_df = df.copy()
        if not chart_df.empty and 'latest_timestamp' in chart_df.columns:
            chart_df['date'] = chart_df['latest_timestamp'].dt.date
            chart_df['current'] = pd.to_numeric(chart_df['current'], errors='coerce')
            chart_df['tide'] = pd.to_numeric(chart_df['tide'], errors='coerce')
            chart_df = chart_df.groupby(['date'])[['current', 'tide']].mean().reset_index()
            chart_df['id_buoy'] = 'Rata-rata Wilayah'
            chart_df['latest_timestamp'] = pd.to_datetime(chart_df['date'])

        chart_df = chart_df.sort_values("latest_timestamp") if not chart_df.empty else pd.DataFrame()
        c1, c2 = st.columns(2)
        with c1:
            st.caption("🌊 Rerata Arus (Current)")
            render_chart(chart_df, 'latest_timestamp', 'current', 'id_buoy', None)
        with c2:
            st.caption("🌊 Rerata Pasang Surut (Tide)")
            render_chart(chart_df, 'latest_timestamp', 'tide', 'id_buoy', None)

        st.caption("⚗️ Densitas")
        page_heatmap(df, "density")


def view_buoy_detail(b_id, name):
    """Renders buoy detail inline — no dialog decorator needed."""
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
            <span style="font-size:1.5rem;">📡</span>
            <div>
                <div style="font-family:'Outfit',sans-serif; font-size:1.1rem; font-weight:800; color:#f0f6ff;">{name}</div>
                <div style="font-size:0.78rem; color:#8ba3c0;">ID: {b_id}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    hist_df = get_buoy_history(b_id)

    if not hist_df.empty:
        hist_df['created_at'] = pd.to_datetime(hist_df['created_at'])
        min_date = hist_df['created_at'].min()
        max_date = hist_df['created_at'].max()

        st.caption("🗓️ Filter Rentang Tanggal")
        d = st.date_input("", [min_date, max_date],
                          min_value=min_date, max_value=max_date,
                          label_visibility="collapsed",
                          key=f"buoy_date_{b_id}")

        filtered_df = hist_df.copy()
        if isinstance(d, (list, tuple)) and len(d) == 2:
            start_date = pd.to_datetime(d[0])
            end_date   = pd.to_datetime(d[1])
            filtered_df = hist_df[
                (hist_df['created_at'] >= start_date) &
                (hist_df['created_at'] <  end_date + pd.Timedelta(days=1))
            ]

        if not filtered_df.empty:
            st.divider()
            st.markdown("#### 📈 Grafik Detail")
            c1, c2 = st.columns(2)
            c3, c4 = st.columns(2)
            with c1:
                st.caption("🧂 Salinitas")
                render_chart(filtered_df, 'created_at', 'salinitas', 'id_buoy', None)
            with c2:
                st.caption("🌫️ Kekeruhan")
                render_chart(filtered_df, 'created_at', 'turbidity', 'id_buoy', None)
            with c3:
                st.caption("💨 Oksigen")
                render_chart(filtered_df, 'created_at', 'oxygen', 'id_buoy', None)
            with c4:
                st.caption("⚗️ Densitas")
                render_chart(filtered_df, 'created_at', 'density', 'id_buoy', None)

            st.divider()
            st.markdown("#### 📄 Data Mentah")
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("Tidak ada data dalam rentang tanggal yang dipilih.")
    else:
        st.warning("Belum ada data historis untuk buoy ini.")


def render_buoy_monitoring():
    _section_header("📡", "Pemantauan Buoy", "Status dan riwayat sensor pelampung")

    buoys_df = get_buoy_fleet()

    if buoys_df.empty:
        st.info("Belum ada data buoy yang aktif.")
        return

    total  = len(buoys_df)
    active = len(buoys_df[buoys_df['status'] == 'Active'])
    maint  = total - active

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Buoy",       total)
    with c2: st.metric("Buoy Aktif",       active)
    with c3: st.metric("Dalam Perawatan",  maint)

    st.divider()

    # Grid 4-col
    cols_per_row = 4
    rows = [buoys_df.iloc[i:i+cols_per_row] for i in range(0, len(buoys_df), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        buoy_list = list(row.iterrows())
        for i, col in enumerate(cols):
            with col:
                if i < len(buoy_list):
                    _, buoy = buoy_list[i]
                    b_id    = buoy['code_buoy']
                    loc     = buoy.get('location') or 'Lokasi ?'
                    status  = buoy['status']
                    batt    = buoy.get('battery', '-')
                    last_up = buoy.get('last_update')
                    fmt_update = last_up.strftime("%d %b %H:%M") if pd.notnull(last_up) else "-"

                    if status == "Maintenance":
                        status_color = "#f59e0b"
                        bg_gradient  = "linear-gradient(145deg, rgba(245,158,11,0.14) 0%, rgba(10,16,32,0.65) 100%)"
                        border_color = "rgba(245,158,11,0.28)"
                    elif status == "Active":
                        status_color = "#22c55e"
                        bg_gradient  = "linear-gradient(145deg, rgba(34,197,94,0.1) 0%, rgba(10,16,32,0.65) 100%)"
                        border_color = "rgba(34,197,94,0.28)"
                    else:
                        status_color = "#8ba3c0"
                        bg_gradient  = "linear-gradient(145deg, rgba(139,163,192,0.08) 0%, rgba(10,16,32,0.65) 100%)"
                        border_color = "rgba(139,163,192,0.18)"

                    html_template = load_html("buoy_card.html")
                    if html_template:
                        card_html = html_template \
                            .replace("{b_id}", str(b_id)) \
                            .replace("{loc}", str(loc)) \
                            .replace("{status}", str(status)) \
                            .replace("{status_color}", status_color) \
                            .replace("{bg_gradient}", bg_gradient) \
                            .replace("{border_color}", border_color) \
                            .replace("{batt}", str(batt)) \
                            .replace("{fmt_update}", str(fmt_update))
                        st.markdown(card_html, unsafe_allow_html=True)
                    else:
                        st.error("Template buoy_card.html missing")

                    if st.button("Detail 🔍", key=f"btn_detail_{b_id}", use_container_width=True):
                        st.session_state['buoy_detail_id']   = b_id
                        st.session_state['buoy_detail_name'] = f"Buoy {b_id} — {loc}"
                else:
                    # Empty slot placeholder
                    st.markdown("""
                        <div style="
                            border: 1px dashed rgba(255,255,255,0.07);
                            border-radius: 20px;
                            height: 180px;
                        "></div>
                    """, unsafe_allow_html=True)


def render_environment_page():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🌊</div>
            <div>
                <p class="page-header-title">Enviro Control</p>
                <p class="page-header-subtitle">Marine environmental monitoring & buoy telemetry</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔥 Grafik Heatmap", "📡 Pemantauan Buoy"])

    with tab1:
        render_environ_heatmap()

    with tab2:
        render_buoy_monitoring()

        # Inline buoy detail panel (replaces dialog)
        if st.session_state.get('buoy_detail_id'):
            st.divider()
            col_title, col_close = st.columns([8, 1])
            with col_close:
                if st.button("✖ Tutup", use_container_width=True):
                    st.session_state['buoy_detail_id']   = None
                    st.session_state['buoy_detail_name'] = None
                    st.rerun()
            view_buoy_detail(
                st.session_state['buoy_detail_id'],
                st.session_state.get('buoy_detail_name', '')
            )
