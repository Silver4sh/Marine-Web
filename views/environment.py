import streamlit as st
import pandas as pd
import altair as alt
from db.repositories.environ_repo import (
    get_data_water, get_buoy_fleet, get_buoy_history,
    get_environmental_compliance_dashboard
)
from components.visualizations import calendar_heatmap
from components.helpers import load_html
from components.charts import gauge_chart
from components.cards import render_metric_card
from services.ai_service import MarineAIAnalyst


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

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


# ─────────────────────────────────────────────────────────────────────────────
# Parameter Metadata
# ─────────────────────────────────────────────────────────────────────────────

_PARAM_META = {
    # cerah (rendah) → pekat (tinggi)
    "salinitas": {"label": "🧂 Salinitas",    "unit": "PSU",  "color": [[0,"rgba(219,234,254,1)"],[0.5,"rgba(59,130,246,0.9)"],[1,"rgba(30,58,138,1)"]]},
    "turbidity": {"label": "🌫️ Kekeruhan",   "unit": "NTU",  "color": [[0,"rgba(254,249,195,1)"],[0.5,"rgba(234,179,8,0.9)"], [1,"rgba(120,53,15,1)"]]},
    "oxygen":    {"label": "💨 Oksigen",      "unit": "mg/L", "color": [[0,"rgba(209,250,229,1)"],[0.5,"rgba(16,185,129,0.9)"],[1,"rgba(6,78,59,1)"]]},
    "density":   {"label": "⚗️ Densitas",    "unit": "σₜ",   "color": [[0,"rgba(237,233,254,1)"],[0.5,"rgba(139,92,246,0.9)"],[1,"rgba(88,28,135,1)"]]},
    "current":   {"label": "🌊 Arus",         "unit": "m/s",  "color": [[0,"rgba(224,242,254,1)"],[0.5,"rgba(14,165,233,0.9)"],[1,"rgba(12,74,110,1)"]]},
    "tide":      {"label": "🌊 Pasang Surut", "unit": "m",    "color": [[0,"rgba(204,251,241,1)"],[0.5,"rgba(20,184,166,0.9)"],[1,"rgba(19,78,74,1)"]]},
}


# ─────────────────────────────────────────────────────────────────────────────
# Pop-up Modal — tampil saat kotak kalender diklik
# ─────────────────────────────────────────────────────────────────────────────

@st.dialog("📈 Detail Data Per Jam", width="large")
def _show_hourly_detail_modal(df: pd.DataFrame, param: str, date_str: str, date_col: str = "latest_timestamp"):
    meta  = _PARAM_META.get(param, {"label": param, "unit": ""})
    label = meta["label"]
    unit  = meta["unit"]

    st.markdown(
        f'<div style="font-family:Outfit,sans-serif;font-size:0.85rem;color:#94a3b8;margin-bottom:12px;">'
        f'Distribusi jam-ke-jam  <strong style="color:#f1f5f9">{label}</strong>  pada  '
        f'<strong style="color:#ef4444">{date_str}</strong></div>',
        unsafe_allow_html=True,
    )

    hourly_df = df.copy()
    if not hourly_df.empty and date_col in hourly_df.columns:
        hourly_df[date_col] = pd.to_datetime(hourly_df[date_col], errors="coerce")
        hourly_df["_date"] = hourly_df[date_col].dt.strftime("%Y-%m-%d")
        subset = hourly_df[hourly_df["_date"] == date_str].copy()

        if not subset.empty:
            subset["_hour"] = subset[date_col].dt.floor("H")
            subset[param]   = pd.to_numeric(subset[param], errors="coerce")
            agg = subset.groupby("_hour")[param].mean().reset_index()
            agg.columns = ["Jam", param]

            if not agg.empty:
                cscale = meta.get("color")
                line_color = cscale[-1][1] if cscale else "#ef4444"

                chart = (
                    alt.Chart(agg)
                    .mark_area(
                        line={"color": line_color, "strokeWidth": 2},
                        color=alt.Gradient(
                            gradient="linear",
                            stops=[
                                alt.GradientStop(color=line_color.replace("1)", "0.3)").replace(")", ",0.3)"), offset=0),
                                alt.GradientStop(color="rgba(14,17,28,0)", offset=1),
                            ],
                            x1=1, x2=1, y1=1, y2=0,
                        ),
                    )
                    .encode(
                        x=alt.X("Jam:T", title="Jam", axis=alt.Axis(format="%H:%M", labelColor="#64748b", tickColor="#64748b", domainColor="#1e293b")),
                        y=alt.Y(f"{param}:Q", title=f"{label} ({unit})", axis=alt.Axis(labelColor="#64748b", gridColor="#1e293b")),
                        tooltip=[
                            alt.Tooltip("Jam:T", title="Jam", format="%H:%M"),
                            alt.Tooltip(f"{param}:Q", title=label, format=".2f"),
                        ],
                    )
                    .properties(height=280)
                    .configure_view(strokeWidth=0)
                    .configure(background="rgba(0,0,0,0)")
                    .interactive()
                )
                st.altair_chart(chart, width='stretch')
            else:
                st.info("Tidak ada nilai valid untuk beragregasi.")
        else:
            st.warning(f"Tidak ada data sensor pada tanggal **{date_str}**.")
    else:
        st.warning("Data tidak tersedia.")


# ─────────────────────────────────────────────────────────────────────────────
# Render satu kotak heatmap + tangkap klik
# ─────────────────────────────────────────────────────────────────────────────

def _render_heatmap_card(df, param: str, date_col="latest_timestamp", height=190,
                         key_suffix="", year=None, month=None):
    """Render GitHub-style yearly heatmap dan kembalikan tanggal yang diklik (atau None)."""
    meta   = _PARAM_META.get(param, {"label": param, "unit": "", "color": None})
    label  = meta["label"]
    unit   = meta["unit"]
    cscale = meta["color"]

    st.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">'
        f'<span style="font-family:Outfit,sans-serif;font-size:0.88rem;font-weight:700;color:#f1f5f9;">{label}</span>'
        f'<span style="font-size:0.70rem;color:#64748b;background:rgba(255,255,255,0.05);'
        f'padding:2px 8px;border-radius:99px;border:1px solid rgba(255,255,255,0.07);">{unit}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    fig   = calendar_heatmap(df, date_col, param, color_scale=cscale, height=height, year=year)
    key   = f"heatmap_{param}_{key_suffix}" if key_suffix else f"heatmap_{param}"
    event = st.plotly_chart(
        fig,
        width='stretch',
        config={"displayModeBar": False, "responsive": True},
        on_select="rerun",
        selection_mode="points",
        key=key,
    )

    if event and "selection" in event and event["selection"].get("points"):
        point = event["selection"]["points"][0]
        cd = point.get("customdata")
        if cd:
            return cd[0] if isinstance(cd, list) else cd
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Tab 1 — Heatmap Kalender
# ─────────────────────────────────────────────────────────────────────────────

def _get_target_year(session_key: str):
    """Hitung tahun target berdasarkan offset di session state."""
    import datetime
    offset = st.session_state.get(session_key, 0)
    return datetime.date.today().year + offset


def _year_nav(session_key: str):
    """Render navigasi tahun ◀ / 2026 / ▶"""
    year = _get_target_year(session_key)
    c_prev, c_lbl, c_next = st.columns([1, 5, 1])
    with c_prev:
        if st.button("◀", key=f"{session_key}_prev", width='stretch'):
            st.session_state[session_key] = st.session_state.get(session_key, 0) - 1
            st.rerun()
    with c_lbl:
        st.markdown(
            f'<div style="text-align:center;font-family:Outfit,sans-serif;font-size:0.92rem;'
            f'font-weight:700;color:#cbd5e1;padding:6px 0;">📅 {year}</div>',
            unsafe_allow_html=True,
        )
    with c_next:
        if st.button("▶", key=f"{session_key}_next", width='stretch'):
            st.session_state[session_key] = st.session_state.get(session_key, 0) + 1
            st.rerun()
    return year


def render_environ_heatmap():
    _section_header(
        "🔥", "Kalender Heatmap",
        "Klik kotak hari untuk melihat detail jam-ke-jam"
    )
    df = get_data_water()

    # AI panel
    anomaly_df = df[df["salinitas"] > 40] if not df.empty and "salinitas" in df.columns else pd.DataFrame()
    ai_env = MarineAIAnalyst.analyze_environment(anomaly_df)
    with st.expander("🤖 AI Eco-Watch", expanded=False):
        for insight in ai_env["insights"]:
            itype = insight.get("type", "info")
            msg   = f"**{insight['title']}**\n\n{insight['desc']}"
            if   itype == "critical": st.error(msg)
            elif itype == "warning":  st.warning(msg)
            elif itype == "positive": st.success(msg)
            else:                     st.info(msg)

    if not df.empty and "latest_timestamp" in df.columns:
        df["latest_timestamp"] = pd.to_datetime(df["latest_timestamp"])

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Navigasi Tahun ────────────────────────────────────────────────────────
    nav_key = f"hmapnav_{cat.replace(' ','_')}"
    year = _year_nav(nav_key)
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if cat == "Kualitas Air":
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            sel = _render_heatmap_card(df, "salinitas", year=year)
            if sel: _show_hourly_detail_modal(df, "salinitas", sel)
        with col2:
            sel = _render_heatmap_card(df, "turbidity", year=year)
            if sel: _show_hourly_detail_modal(df, "turbidity", sel)
        sel = _render_heatmap_card(df, "oxygen", year=year)
        if sel: _show_hourly_detail_modal(df, "oxygen", sel)

    else:  # Oseanografi
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            sel = _render_heatmap_card(df, "current", year=year)
            if sel: _show_hourly_detail_modal(df, "current", sel)
        with col2:
            sel = _render_heatmap_card(df, "tide", year=year)
            if sel: _show_hourly_detail_modal(df, "tide", sel)
        sel = _render_heatmap_card(df, "density", year=year)
        if sel: _show_hourly_detail_modal(df, "density", sel)


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
        hist_df["created_at"] = pd.to_datetime(hist_df["created_at"])
        min_date = hist_df["created_at"].min()
        max_date = hist_df["created_at"].max()

        st.caption("🗓️ Filter Rentang Tanggal")
        d = st.date_input("", [min_date, max_date],
                          min_value=min_date, max_value=max_date,
                          label_visibility="collapsed",
                          key=f"buoy_date_{b_id}")

        filtered_df = hist_df.copy()
        if isinstance(d, (list, tuple)) and len(d) == 2:
            filtered_df = hist_df[
                (hist_df["created_at"] >= pd.to_datetime(d[0])) &
                (hist_df["created_at"] <  pd.to_datetime(d[1]) + pd.Timedelta(days=1))
            ]

        if not filtered_df.empty:
            st.divider()
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.95rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:10px;">
                         📅 Kalender Heatmap (Klik untuk detail)</div>""", unsafe_allow_html=True)

            col1, col2 = st.columns(2, gap="medium")
            with col1:
                sel = _render_heatmap_card(filtered_df, "salinitas", date_col="created_at", height=175, key_suffix=b_id)
                if sel: _show_hourly_detail_modal(filtered_df, "salinitas", sel, date_col="created_at")
            with col2:
                sel = _render_heatmap_card(filtered_df, "turbidity", date_col="created_at", height=175, key_suffix=b_id)
                if sel: _show_hourly_detail_modal(filtered_df, "turbidity", sel, date_col="created_at")

            col3, col4 = st.columns(2, gap="medium")
            with col3:
                sel = _render_heatmap_card(filtered_df, "oxygen",  date_col="created_at", height=175, key_suffix=b_id)
                if sel: _show_hourly_detail_modal(filtered_df, "oxygen", sel, date_col="created_at")
            with col4:
                sel = _render_heatmap_card(filtered_df, "density", date_col="created_at", height=175, key_suffix=b_id)
                if sel: _show_hourly_detail_modal(filtered_df, "density", sel, date_col="created_at")

            st.divider()
            st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:0.95rem;
                         font-weight:700;color:#f1f5f9;margin-bottom:10px;">
                         📄 Data Mentah</div>""", unsafe_allow_html=True)
            st.dataframe(filtered_df, width='stretch')
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
    active = len(buoys_df[buoys_df["status"] == "Active"])
    maint  = total - active

    comp_df    = get_environmental_compliance_dashboard()
    comp_score = 100.0
    if not comp_df.empty and "compliance_score_pct" in comp_df.columns:
        val = comp_df["compliance_score_pct"].iloc[0]
        if val is not None:
            comp_score = round(float(val), 1)

    c1, c2, c3, c4 = st.columns([1, 1, 1, 1.5])
    with c1: render_metric_card("Total Buoy",  total,  None, "#ef4444")
    with c2: render_metric_card("Buoy Aktif",  active, None, "#22c55e")
    with c3: render_metric_card("Perawatan",   maint,  None, "#f59e0b")
    with c4:
        st.plotly_chart(
            gauge_chart(comp_score, "Kepatuhan Lingkungan", 100, "%", 
                        thresholds=(75, 90), height=160),
            config={"displayModeBar": False, "responsive": True},
            width='stretch',
        )

    st.divider()

    cols_per_row = 4
    rows = [buoys_df.iloc[i:i+cols_per_row] for i in range(0, len(buoys_df), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row, gap="small")
        buoy_list = list(row.iterrows())
        for i, col in enumerate(cols):
            with col:
                if i < len(buoy_list):
                    _, buoy = buoy_list[i]
                    b_id    = buoy["code_buoy"]
                    loc     = buoy.get("location") or "Lokasi ?"
                    status  = buoy["status"]
                    batt    = buoy.get("battery", "-")
                    last_up = pd.to_datetime(buoy.get("last_update"), errors="coerce")
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

                    if st.button("Detail 🔍", key=f"btn_detail_{b_id}", width='stretch'):
                        st.session_state["buoy_detail_id"]   = b_id
                        st.session_state["buoy_detail_name"] = f"Buoy {b_id} — {loc}"
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

        if st.session_state.get("buoy_detail_id"):
            st.divider()
            col_title, col_close = st.columns([9, 1])
            with col_close:
                if st.button("✖ Tutup", width='stretch'):
                    st.session_state["buoy_detail_id"]   = None
                    st.session_state["buoy_detail_name"] = None
                    st.rerun()
            view_buoy_detail(
                st.session_state["buoy_detail_id"],
                st.session_state.get("buoy_detail_name", ""),
            )

