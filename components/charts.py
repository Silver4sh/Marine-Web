import plotly.graph_objects as go
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Base chart theme
# ─────────────────────────────────────────────────────────────────────────────
_COLORS = ["#ef4444", "#f59e0b", "#fb923c", "#f472b6", "#60a5fa", "#22c55e"]

def apply_chart_style(fig, title: str = None) -> go.Figure:
    """
    Apply the MarineOS dark-mode Plotly theme — Red & Gold command palette.
    Call this on any Figure before rendering.
    """
    layout_args = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=12, color="#94a3b8"),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(255,255,255,0.08)",
            tickfont=dict(family="Inter", size=11, color="#94a3b8"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(family="Inter", size=11, color="#94a3b8"),
        ),
        legend=dict(
            orientation="h",
            y=1.1,
            x=0,
            xanchor="left",
            font=dict(family="Inter", size=11, color="#94a3b8"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=60, l=10, r=10, b=10),
        hovermode="x unified",
        colorway=_COLORS,
    )

    if title:
        layout_args["title"] = dict(
            text=title,
            font=dict(family="Outfit", size=17, color="#f1f5f9"),
            x=0,
            xanchor="left",
        )
    else:
        layout_args["title"] = dict(text="", font=dict(size=1))

    fig.update_layout(**layout_args)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(10,12,22,0.96)",
            bordercolor="rgba(239,68,68,0.28)",
            font=dict(family="Inter", color="#ffffff"),
        )
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# Gauge / Indicator chart
# ─────────────────────────────────────────────────────────────────────────────

def gauge_chart(
    value: float,
    title: str,
    max_val: float = 100,
    suffix: str = "%",
    thresholds: tuple = (50, 80),          # (warning, good) thresholds
    height: int = 200,
) -> go.Figure:
    """
    Premium arc-style gauge (Plotly Indicator).

    Colour bands:
        red    → 0 to thresholds[0]
        orange → thresholds[0] to thresholds[1]
        green  → thresholds[1] to max_val
    """
    warn, good = thresholds
    bar_color  = "#22c55e" if value >= good else ("#f59e0b" if value >= warn else "#f43f5e")

    fig = go.Figure(go.Indicator(
        mode    = "gauge+number+delta" if value > 0 else "gauge+number",
        value   = round(value, 1),
        number  = dict(suffix=suffix, font=dict(color="#f0f6ff", family="Outfit", size=32)),
        gauge   = dict(
            axis       = dict(range=[0, max_val], tickcolor="#475569",
                              tickfont=dict(size=10, color="#64748b")),
            bar        = dict(color=bar_color, thickness=0.75),
            bgcolor    = "rgba(255,255,255,0.03)",
            bordercolor= "rgba(255,255,255,0.06)",
            borderwidth= 1,
            steps       = [
                dict(range=[0,      warn],    color="rgba(244,63,94,0.12)"),
                dict(range=[warn,   good],    color="rgba(245,158,11,0.12)"),
                dict(range=[good,   max_val], color="rgba(34,197,94,0.12)"),
            ],
            threshold  = dict(
                line =dict(color="#38bdf8", width=3),
                thickness=0.85,
                value=value,
            ),
        ),
        title   = dict(text=title, font=dict(family="Outfit", size=14, color="#94a3b8")),
        domain  = dict(x=[0, 1], y=[0, 1]),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor ="rgba(0,0,0,0)",
        margin       =dict(t=30, b=0, l=10, r=10),
        height       =height,
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# KPI progress bar (HTML-based, inline)
# ─────────────────────────────────────────────────────────────────────────────

def kpi_progress_bar(
    label: str,
    current: float,
    target: float,
    prefix: str = "Rp ",
    suffix: str = "",
) -> None:
    """
    Render an animated KPI progress bar as a Streamlit HTML component.

    Args:
        label:   Display label (e.g. "Pendapatan Bulan Ini")
        current: Achieved value
        target:  Target value (must be > 0)
        prefix:  Currency / unit prefix shown before the value
        suffix:  Unit suffix shown after the value
    """
    if target <= 0:
        return

    pct = min((current / target) * 100, 100)
    color = "#22c55e" if pct >= 80 else ("#f59e0b" if pct >= 50 else "#f43f5e")
    glow  = f"0 0 8px {color}66"

    # Format numbers
    def _fmt(v):
        if v >= 1e9:  return f"{v/1e9:.1f}M"
        if v >= 1e6:  return f"{v/1e6:.0f}jt"
        return f"{v:,.0f}"

    cur_str = f"{prefix}{_fmt(current)}{suffix}"
    tgt_str = f"{prefix}{_fmt(target)}{suffix}"

    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div style="font-family:'Outfit',sans-serif; font-size:0.85rem; color:#94a3b8; font-weight:600;">
                {label}
            </div>
            <div style="font-family:'Outfit',sans-serif; font-size:0.95rem; font-weight:800; color:{color};">
                {pct:.1f}%
            </div>
        </div>
        <div style="
            background: rgba(255,255,255,0.06);
            border-radius: 99px;
            height: 10px;
            overflow: hidden;
            margin-bottom: 8px;
        ">
            <div style="
                width: {pct}%;
                height: 100%;
                background: linear-gradient(90deg, {color}aa, {color});
                border-radius: 99px;
                box-shadow: {glow};
                transition: width 0.8s ease-in-out;
            "></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:#64748b;">
            <span>Realisasi: <strong style="color:#cbd5e1;">{cur_str}</strong></span>
            <span>Target: <strong style="color:#cbd5e1;">{tgt_str}</strong></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Task 4 — Dredging Charts
# ─────────────────────────────────────────────────────────────────────────────

def seabed_crosssection_chart(
    distance_m=None,
    before_depth=None,
    after_depth=None,
    title="✂️ Profil Potongan Melintang Dasar Laut",
) -> go.Figure:
    """
    Grafik cross-section dasar laut sebelum (abu-abu) vs sesudah (teal) pengerukan.

    Args:
        distance_m   : list jarak horizontal (m). Default: 0–500m, 20 titik.
        before_depth : list kedalaman sebelum dikeruk (negatif = di bawah LWS).
        after_depth  : list kedalaman sesudah dikeruk.
    """
    import numpy as np
    if distance_m is None:
        distance_m = list(range(0, 501, 25))
    n = len(distance_m)
    if before_depth is None:
        np.random.seed(42)
        before_depth = [-3.0 - np.random.uniform(0, 1.5) - 0.8 * abs(i - n // 2) / (n // 2)
                       for i in range(n)]
    if after_depth is None:
        after_depth = [b - np.random.uniform(1.5, 3.0) for b in before_depth]

    fig = go.Figure()

    # Before fill (sedimen abu-abu)
    fig.add_trace(go.Scatter(
        x=distance_m, y=before_depth,
        fill="tozeroy",
        fillcolor="rgba(74,104,130,0.25)",
        line=dict(color="#4a6882", width=2, dash="dot"),
        name="Sebelum Keruk",
        hovertemplate="Jarak: %{x}m<br>Kedalaman: %{y:.1f}m LWS<extra></extra>",
    ))

    # After fill (bersih — teal)
    fig.add_trace(go.Scatter(
        x=distance_m, y=after_depth,
        fill="tozeroy",
        fillcolor="rgba(45,212,191,0.18)",
        line=dict(color="#2DD4BF", width=2.5),
        name="Sesudah Keruk",
        hovertemplate="Jarak: %{x}m<br>Kedalaman: %{y:.1f}m LWS<extra></extra>",
    ))

    # Target line
    target_val = min(after_depth)
    fig.add_hline(
        y=target_val,
        line=dict(color="#E9C46A", width=1.5, dash="dash"),
        annotation_text=f"Target: {target_val:.1f}m LWS",
        annotation_position="top right",
        annotation_font=dict(color="#E9C46A", size=10),
    )

    apply_chart_style(fig, title=title)
    fig.update_layout(
        height=280,
        yaxis=dict(title="Kedalaman (m LWS)", autorange=True),
        xaxis=dict(title="Jarak Horizontal (m)"),
        legend=dict(orientation="h", y=1.12, x=0),
        hovermode="x unified",
        margin=dict(t=55, l=50, r=16, b=42),
    )
    return fig


def dredging_gantt_chart(schedule_data=None, title="📅 Jadwal Pengerukan Zona") -> go.Figure:
    """
    Gantt-style timeline chart untuk jadwal pengerukan multi-zona.
    schedule_data: list of dicts with keys: zone, start, end, status
    """
    import plotly.express as px
    from datetime import datetime, timedelta

    if schedule_data is None:
        base = datetime(2025, 3, 1)
        schedule_data = [
            {"Zona": "Zona A", "Mulai": base,               "Selesai": base + timedelta(days=18),
             "Status": "Selesai",  "Volume (m³)": 12000},
            {"Zona": "Zona B", "Mulai": base + timedelta(days=12), "Selesai": base + timedelta(days=35),
             "Status": "Aktif",    "Volume (m³)": 8500},
            {"Zona": "Zona C", "Mulai": base + timedelta(days=30), "Selesai": base + timedelta(days=55),
             "Status": "Terjadwal","Volume (m³)": 15000},
            {"Zona": "Zona D", "Mulai": base + timedelta(days=50), "Selesai": base + timedelta(days=70),
             "Status": "Terjadwal","Volume (m³)": 9200},
        ]
    import pandas as pd
    df = pd.DataFrame(schedule_data)

    color_map = {
        "Selesai":   "#2DD4BF",
        "Aktif":     "#FACC15",
        "Terjadwal": "#4a6882",
        "Tunda":     "#F97316",
    }

    fig = px.timeline(
        df,
        x_start="Mulai", x_end="Selesai",
        y="Zona", color="Status",
        color_discrete_map=color_map,
        hover_data={"Volume (m³)": True, "Status": True},
        labels={"Zona": "", "Mulai": "Mulai", "Selesai": "Selesai"},
    )
    fig.update_yaxes(autorange="reversed")
    apply_chart_style(fig, title=title)
    fig.update_layout(
        height=260,
        margin=dict(t=55, l=70, r=16, b=30),
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis_title="",
    )
    return fig


def water_quality_scatter(
    df=None,
    op_col="jam_operasi",
    ntu_col="turbidity_ntu",
    tss_col="tss_mgl",
    vol_col="volume_m3",
    title="💧 Kualitas Air vs Operasional",
) -> go.Figure:
    """
    Scatter plot: jam operasional pengerukan vs kekeruhan (NTU).
    Ukuran titik = volume pasir diangkat. Warna = status compliance.
    """
    import numpy as np
    if df is None or df.empty if hasattr(df, "empty") else df is None:
        import pandas as pd
        np.random.seed(7)
        hrs = np.arange(0, 24, 0.5)
        ntu = 15 + 25 * np.sin(np.pi * hrs / 12) + np.random.normal(0, 5, len(hrs))
        tss = ntu * 1.8 + np.random.normal(0, 8, len(hrs))
        vol = np.random.uniform(50, 400, len(hrs))
        df = pd.DataFrame({op_col: hrs, ntu_col: ntu, tss_col: tss, vol_col: vol})

    limit = 50.0
    df["_color"] = df[ntu_col].apply(
        lambda v: "#2DD4BF" if v <= limit else ("#FACC15" if v <= limit * 1.6 else "#F97316")
    )
    df["_label"] = df[ntu_col].apply(
        lambda v: "Aman" if v <= limit else ("Waspada" if v <= limit * 1.6 else "Melanggar")
    )

    fig = go.Figure()
    for status, clr in [("Aman", "#2DD4BF"), ("Waspada", "#FACC15"), ("Melanggar", "#F97316")]:
        sub = df[df["_label"] == status]
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub[op_col], y=sub[ntu_col],
            mode="markers",
            name=status,
            marker=dict(
                size=sub[vol_col] / sub[vol_col].max() * 22 + 6,
                color=clr,
                opacity=0.78,
                line=dict(width=1, color="rgba(255,255,255,0.25)"),
            ),
            hovertemplate=(
                f"Jam: %{{x:.1f}}<br>{ntu_col}: %{{y:.1f}} NTU<br>"
                f"Volume: %{{customdata:.0f}} m³<extra>{status}</extra>"
            ),
            customdata=sub[vol_col],
        ))

    # Batas limit line
    fig.add_hline(
        y=limit, line=dict(color="#FACC15", width=1.5, dash="dash"),
        annotation_text="Batas 50 NTU",
        annotation_font=dict(color="#FACC15", size=10),
    )

    apply_chart_style(fig, title=title)
    fig.update_layout(
        height=300,
        xaxis=dict(title="Jam Operasional"),
        yaxis=dict(title="Turbidity (NTU)"),
        margin=dict(t=55, l=50, r=16, b=42),
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig

