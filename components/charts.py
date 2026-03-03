import plotly.graph_objects as go
import streamlit as st


# ─────────────────────────────────────────────────────────────────────────────
# Base chart theme
# ─────────────────────────────────────────────────────────────────────────────
_COLORS = ["#22d3ee", "#a78bfa", "#f472b6", "#a3e635", "#fbbf24", "#fb923c"]

def apply_chart_style(fig, title: str = None) -> go.Figure:
    """
    Apply the MarineOS dark-mode Plotly theme.
    Call this on any Figure before rendering.
    """
    layout_args = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Plus Jakarta Sans", size=12, color="#94a3b8"),
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(255,255,255,0.1)",
            tickfont=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.05)",
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1"),
        ),
        legend=dict(
            orientation="h",
            y=1.1,
            x=0,
            xanchor="left",
            font=dict(family="Plus Jakarta Sans", size=11, color="#cbd5e1"),
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=60, l=10, r=10, b=10),
        hovermode="x unified",
        colorway=_COLORS,
    )

    if title:
        layout_args["title"] = dict(
            text=title,
            font=dict(family="Outfit", size=18, weight=600, color="#f8fafc"),
            x=0,
            xanchor="left",
        )
    else:
        layout_args["title"] = dict(text="", font=dict(size=1))

    fig.update_layout(**layout_args)
    fig.update_traces(
        hoverlabel=dict(
            bgcolor="rgba(15,23,42,0.9)",
            bordercolor="rgba(148,163,184,0.2)",
            font=dict(family="Plus Jakarta Sans", color="#ffffff"),
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
