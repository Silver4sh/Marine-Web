import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
from db.repositories.environ_repo import (
    get_data_water, get_buoy_fleet, get_buoy_history,
    get_environmental_compliance_dashboard
)
from components.visualizations import calendar_heatmap
from components.helpers import load_html
from components.charts import apply_chart_style, gauge_chart
from components.cards import render_metric_card
from services.ai_service import MarineAIAnalyst


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _render_line_chart(df, x_col, y_col, color_col, title=""):
    """Altair line chart, full-width, dark themed."""
    if df.empty or y_col not in df.columns:
        st.info("Tidak ada data untuk ditampilkan.")
        return

    chart = (
        alt.Chart(df)
        .mark_line(point=alt.OverlayMarkDef(size=30, opacity=0.7))
        .encode(
            x=alt.X(x_col, title="Waktu", axis=alt.Axis(labelColor="#64748b", tickColor="#64748b", domainColor="#1e293b")),
            y=alt.Y(y_col, title="", axis=alt.Axis(labelColor="#64748b", gridColor="#1e293b")),
            color=alt.Color(color_col, legend=None, scale=alt.Scale(scheme="reds")),
            tooltip=[x_col, y_col, color_col],
        )
        .properties(height=220)
        .configure_view(strokeWidth=0)
        .configure(background="rgba(0,0,0,0)")
        .interactive()
    )
    if title:
        chart = chart.properties(title=alt.TitleParams(title, color="#94a3b8", fontSize=12, font="Outfit"))

    st.altair_chart(chart, use_container_width=True)


def _section_header(icon: str, title: str, subtitle: str = ""):
    sub = f'<div style="font-size:0.78rem;color:#64748b;margin-top:2px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;margin-top:8px;
                    padding-bottom:10px;border-bottom:1px solid rgba(239,68,68,0.10);">
            <div style="
                width:34px;height:34px;border-radius:8px;
                background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.25);
                display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;
            ">{icon}</div>
            <div>
                <div style="font-family:'Outfit',sans-serif;font-size:1rem;font-weight:800;
                            color:#f1f5f9;letter-spacing:-0.01em;">{title}</div>
                {sub}
            </div>
        </div>
    """, unsafe_allow_html=True)


def _card_wrap(content_fn, *args, **kwargs):
    """Thin styled wrapper around content."""
    st.markdown('<div style="background:rgba(18,22,38,0.80);border:1px solid rgba(255,255,255,0.06);'
                'border-radius:14px;padding:16px 20px;margin-bottom:14px;">', unsafe_allow_html=True)
    content_fn(*args, **kwargs)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Calendar heatmap section  (replaces old Folium page_heatmap)
# ─────────────────────────────────────────────────────────────────────────────

_PARAM_META = {
    "salinitas":  {"label": "🧂 Salinitas",     "unit": "PSU",  "color": [[0,"rgba(20,24,38,0.9)"],[0.5,"rgba(30,58,138,0.9)"],[1,"rgba(96,165,250,1)"]],  },
    "turbidity":  {"label": "🌫️ Kekeruhan",    "unit": "NTU",  "color": [[0,"rgba(20,24,38,0.9)"],[0.5,"rgba(120,53,15,0.9)"],[1,"rgba(251,191,36,1)"]],   },
    "oxygen":     {"label": "💨 Oksigen",       "unit": "mg/L", "color": [[0,"rgba(20,24,38,0.9)"],[0.5,"rgba(5,150,105,0.8)"],[1,"rgba(110,231,183,1)"]],  },
    "density":    {"label": "⚗️ Densitas",     "unit": "σₜ",   "color": None,  },
    "current":    {"label": "🌊 Arus",          "unit": "m/s",  "color": None,  },
    "tide":       {"label": "🌊 Pasang Surut",  "unit": "m",    "color": None,  },
}


def _render_calendar_heatmap_card(df, param: str, date_col="latest_timestamp", height=190):
    """Render one calendar heatmap inside a dark card."""
    meta  = _PARAM_META.get(param, {"label": param, "unit": "", "color": None})
    label = meta["label"]
    unit  = meta["unit"]
    cscale = meta["color"]   # None → default red palette

    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <div style="font-family:'Outfit',sans-serif;font-size:0.88rem;font-weight:700;color:#f1f5f9;">
                {label}
            </div>
            <span style="font-size:0.70rem;color:#64748b;background:rgba(255,255,255,0.05);
                         padding:2px 8px;border-radius:99px;border:1px solid rgba(255,255,255,0.07);">
                {unit}
            </span>
        </div>
    """, unsafe_allow_html=True)

    fig = calendar_heatmap(df, date_col, param, color_scale=cscale, height=height)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Heatmap
# ─────────────────────────────────────────────────────────────────────────────

def render_environ_heatmap():
    _section_header("🔥", "Kalender Heatmap", "Distribusi nilai harian parameter lingkungan")
    df = get_data_water()

    # AI Analysis
    anomaly_df = df[df['salinitas'] > 40] if not df.empty and 'salinitas' in df.columns else pd.DataFrame()
    ai_env = MarineAIAnalyst.analyze_environment(anomaly_df)

    with st.expander("🤖 AI Eco-Watch", expanded=False):
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

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if cat == "Kualitas Air":
        # ── Row 1: two side by side ─────────────────────────────────────────
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            with st.container():
                _render_calendar_heatmap_card(df, "salinitas")
        with col2:
            with st.container():
                _render_calendar_heatmap_card(df, "turbidity")

        # ── Row 2: full width ────────────────────────────────────────────────
        _render_calendar_heatmap_card(df, "oxygen", height=200)

    else:
        # Oseanografi: aggregate current & tide by date first for line charts
        chart_df = df.copy()
        if not chart_df.empty and 'latest_timestamp' in chart_df.columns:
            chart_df['date']    = chart_df['latest_timestamp'].dt.date
            chart_df['current'] = pd.to_numeric(chart_df.get('current', pd.Series(dtype=float)), errors='coerce')
            chart_df['tide']    = pd.to_numeric(chart_df.get('tide',    pd.Series(dtype=float)), errors='coerce')
            chart_df = chart_df.groupby('date')[['current', 'tide']].mean().reset_index()
            chart_df['id_buoy']          = 'Rata-rata Wilayah'
            chart_df['latest_timestamp'] = pd.to_datetime(chart_df['date'])
        chart_df = chart_df.sort_values("latest_timestamp") if not chart_df.empty else pd.DataFrame()

        # Line charts row
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.88rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:6px;">🌊 Rerata Arus</div>""",
                        unsafe_allow_html=True)
            _render_line_chart(chart_df, 'latest_timestamp', 'current', 'id_buoy')
        with col2:
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.88rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:6px;">🌊 Pasang Surut</div>""",
                        unsafe_allow_html=True)
            _render_line_chart(chart_df, 'latest_timestamp', 'tide', 'id_buoy')

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        # Density calendar heatmap: full width
        _render_calendar_heatmap_card(df, "density", height=200)


# ─────────────────────────────────────────────────────────────────────────────
# Buoy detail panel
# ─────────────────────────────────────────────────────────────────────────────

def view_buoy_detail(b_id, name):
    """Renders buoy detail inline."""
    st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;
                    padding:14px 18px;background:rgba(239,68,68,0.06);
                    border:1px solid rgba(239,68,68,0.15);border-radius:12px;">
            <span style="font-size:1.5rem;">📡</span>
            <div>
                <div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:800;color:#f1f5f9;">{name}</div>
                <div style="font-size:0.78rem;color:#64748b;margin-top:2px;">ID: {b_id}</div>
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
            filtered_df = hist_df[
                (hist_df['created_at'] >= pd.to_datetime(d[0])) &
                (hist_df['created_at'] <  pd.to_datetime(d[1]) + pd.Timedelta(days=1))
            ]

        if not filtered_df.empty:
            st.divider()

            # ── Calendar heatmaps ──────────────────────────────────────────
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.95rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:10px;">
                         📅 Kalender Heatmap</div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="medium")
            with col1:
                _render_calendar_heatmap_card(filtered_df, "salinitas", date_col="created_at", height=175)
            with col2:
                _render_calendar_heatmap_card(filtered_df, "turbidity", date_col="created_at", height=175)

            col3, col4 = st.columns(2, gap="medium")
            with col3:
                _render_calendar_heatmap_card(filtered_df, "oxygen",  date_col="created_at", height=175)
            with col4:
                _render_calendar_heatmap_card(filtered_df, "density", date_col="created_at", height=175)

            st.divider()
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.95rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:10px;">
                         📄 Data Mentah</div>""", unsafe_allow_html=True)
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.info("Tidak ada data dalam rentang tanggal yang dipilih.")
    else:
        st.warning("Belum ada data historis untuk buoy ini.")


# ─────────────────────────────────────────────────────────────────────────────
# Tab 2 — Buoy monitoring
# ─────────────────────────────────────────────────────────────────────────────

def render_buoy_monitoring():
    _section_header("📡", "Pemantauan Buoy", "Status dan riwayat sensor pelampung")

    buoys_df = get_buoy_fleet()

    if buoys_df.empty:
        st.info("Belum ada data buoy yang aktif.")
        return

    total  = len(buoys_df)
    active = len(buoys_df[buoys_df['status'] == 'Active'])
    maint  = total - active

    # Compliance gauge
    comp_df    = get_environmental_compliance_dashboard()
    comp_score = 100.0
    if not comp_df.empty and 'compliance_score_pct' in comp_df.columns:
        val = comp_df['compliance_score_pct'].iloc[0]
        if val is not None:
            comp_score = round(float(val), 1)

    # Metric row
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.5])
    with c1:
        render_metric_card("Total Buoy",  total,  "",                      "#ef4444")
    with c2:
        render_metric_card("Buoy Aktif",  active, "Online & Transmitting", "#22c55e")
    with c3:
        render_metric_card("Perawatan",   maint,  "Offline / MTC",         "#f59e0b")
    with c4:
        st.plotly_chart(
            gauge_chart(comp_score, "Kepatuhan Lingkungan", 100, "%",
                        thresholds=(75, 90), height=160),
            config={"displayModeBar": False},
            use_container_width=True,
        )

    st.divider()

    # Buoy grid (4 per row)
    cols_per_row = 4
    rows = [buoys_df.iloc[i:i+cols_per_row] for i in range(0, len(buoys_df), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row, gap="small")
        buoy_list = list(row.iterrows())
        for i, col in enumerate(cols):
            with col:
                if i < len(buoy_list):
                    _, buoy = buoy_list[i]
                    b_id    = buoy['code_buoy']
                    loc     = buoy.get('location') or 'Lokasi ?'
                    status  = buoy['status']
                    batt    = buoy.get('battery', '-')
                    last_up = pd.to_datetime(buoy.get('last_update'), errors="coerce")
                    fmt_update = last_up.strftime("%d %b %H:%M") if pd.notnull(last_up) else "-"

                    if status == "Maintenance":
                        status_color = "#f59e0b"
                        bg_gradient  = "linear-gradient(145deg,rgba(245,158,11,0.14),rgba(10,16,32,0.85))"
                        border_color = "rgba(245,158,11,0.28)"
                    elif status == "Active":
                        status_color = "#22c55e"
                        bg_gradient  = "linear-gradient(145deg,rgba(34,197,94,0.10),rgba(10,16,32,0.85))"
                        border_color = "rgba(34,197,94,0.28)"
                    else:
                        status_color = "#64748b"
                        bg_gradient  = "linear-gradient(145deg,rgba(100,116,139,0.08),rgba(10,16,32,0.85))"
                        border_color = "rgba(100,116,139,0.18)"

                    html_template = load_html("buoy_card.html")
                    if html_template:
                        card_html = (html_template
                            .replace("{b_id}",         str(b_id))
                            .replace("{loc}",           str(loc))
                            .replace("{status}",        str(status))
                            .replace("{status_color}",  status_color)
                            .replace("{bg_gradient}",   bg_gradient)
                            .replace("{border_color}",  border_color)
                            .replace("{batt}",          str(batt))
                            .replace("{fmt_update}",    str(fmt_update))
                        )
                        st.markdown(card_html, unsafe_allow_html=True)

                    if st.button("Detail 🔍", key=f"btn_detail_{b_id}", use_container_width=True):
                        st.session_state['buoy_detail_id']   = b_id
                        st.session_state['buoy_detail_name'] = f"Buoy {b_id} — {loc}"
                else:
                    st.markdown("""<div style="border:1px dashed rgba(255,255,255,0.05);
                                border-radius:14px;height:180px;"></div>""",
                                unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def render_environment_page():
    st.markdown("""
        <div class="page-header">
            <div class="page-header-icon">🌊</div>
            <div>
                <p class="page-header-title">Enviro Control</p>
                <p class="page-header-subtitle">Marine environmental monitoring &amp; buoy telemetry</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📅 Kalender Heatmap", "📡 Pemantauan Buoy"])

    with tab1:
        render_environ_heatmap()

    with tab2:
        render_buoy_monitoring()

        # Inline buoy detail panel
        if st.session_state.get('buoy_detail_id'):
            st.divider()
            col_title, col_close = st.columns([9, 1])
            with col_close:
                if st.button("✖ Tutup", use_container_width=True):
                    st.session_state['buoy_detail_id']   = None
                    st.session_state['buoy_detail_name'] = None
                    st.rerun()
            view_buoy_detail(
                st.session_state['buoy_detail_id'],
                st.session_state.get('buoy_detail_name', '')
            )
