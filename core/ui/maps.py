from core.ui.helpers import get_status_color, create_google_arrow_icon, create_dredger_icon, create_sand_marker_icon, create_dumping_icon
from core.ui.cards import render_vessel_list_column, render_vessel_detail_section
from db.repos.fleet import get_vessel_position, get_path_vessel
from core.config import inject_custom_css
from folium.plugins import MarkerCluster, HeatMap
from folium import Element
from streamlit_folium import st_folium

import folium
import numpy as np
import pandas as pd
import streamlit as st


# ---------------------------------------------------------------------------
# Helper: Haversine distance in metres between two lat/lng points
# ---------------------------------------------------------------------------
def _haversine_m(lat0, lon0, lat1, lon1):
    R = 6371000
    dlat, dlon = np.radians(lat1 - lat0), np.radians(lon1 - lon0)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat0)) * np.cos(np.radians(lat1)) * np.sin(dlon / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


# ---------------------------------------------------------------------------
# Speed-aware animation durations (ms) per segment
# Faster vessel → shorter duration; capped so total ≤ MAX_TOTAL_MS
# ---------------------------------------------------------------------------
def _calc_durations(rows: list, max_total_ms: int = 25000) -> list:
    durations = []
    for i in range(len(rows) - 1):
        r0, r1 = rows[i][1], rows[i + 1][1]
        dist_m = _haversine_m(float(r0['latitude']), float(r0['longitude']),
                               float(r1['latitude']), float(r1['longitude']))
        spd_ms = max(float(r0.get('speed', 0) or 0), 0.1) * 0.514444  # knots → m/s
        seg_ms = int(dist_m / spd_ms * 1000)
        durations.append(max(200, min(seg_ms, 30000)))

    total = sum(durations)
    if total > max_total_ms:
        scale = max_total_ms / total
        durations = [max(200, int(d * scale)) for d in durations]
    return durations or [1000]


# ---------------------------------------------------------------------------
# Add static path + animated moving marker to map
# ---------------------------------------------------------------------------
def add_history_path_to_map(m, path_df, fill_color, v_id_str, show_timelapse=False):
    if path_df.empty:
        return

    path_sorted = path_df.sort_values("created_at")
    path_points = path_sorted[['latitude', 'longitude']].values.tolist()

    # Static track line
    folium.PolyLine(path_points, color=fill_color, weight=3, opacity=0.7,
                    tooltip=f"Jalur {v_id_str}").add_to(m)

    # Last-position arrow marker
    last_row = path_sorted.iloc[-1]
    folium.Marker(
        [last_row['latitude'], last_row['longitude']],
        icon=create_google_arrow_icon(last_row.get('heading', 0), fill_color),
        popup=f"Posisi Terakhir: {last_row['created_at']}"
    ).add_to(m)

    if not show_timelapse or len(path_df) < 2:
        return

    rows_list = list(path_sorted.iterrows())

    # Build JS waypoint data
    waypoints = []
    for _, row in rows_list:
        ts  = row['created_at'].strftime("%H:%M:%S") if pd.notnull(row['created_at']) else "?"
        spd = float(row.get('speed', 0) or 0)
        hdg = row.get('heading', 0)  # pre-extract to avoid backslash in f-string (Python < 3.12)
        lat = row['latitude']
        lon = row['longitude']
        waypoints.append(
            f"{{latlng:[{lat},{lon}],time:'{ts}',loc:'Speed: {spd:.1f} kn | Hdg: {hdg}&deg;'}}"
        )
    waypoints_js = ",\n".join(waypoints)
    durations_js = ", ".join(map(str, _calc_durations(rows_list)))

    map_id = m.get_name()

    # Read MovingMarker.js source to inline it — eliminates any CDN / static-serve race
    import os as _os
    _plugin_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                                 "static", "MovingMarker.js")
    try:
        with open(_plugin_path, "r", encoding="utf-8") as _f:
            _moving_marker_src = _f.read()
    except FileNotFoundError:
        # Fallback: load from parent project dir
        _fallback = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))),
                                  "MovingMarker.js")
        with open(_fallback, "r", encoding="utf-8") as _f:
            _moving_marker_src = _f.read()


    hud_html = f"""
    <style>
        .hud-wrap {{
            position:absolute; bottom:28px; left:50%; transform:translateX(-50%);
            background:rgba(13,20,36,0.90); padding:13px 20px;
            border:1px solid rgba(56,189,248,0.25); border-radius:12px;
            z-index:9999; width:65%; max-width:560px;
            font-family:'Courier New',monospace; color:#94a3b8;
            backdrop-filter:blur(10px); box-shadow:0 4px 20px rgba(0,0,0,0.45);
        }}
        .hud-time {{
            text-align:center; font-size:1.1rem; font-weight:bold;
            color:#7dd3fc; margin-bottom:2px;
        }}
        .hud-info {{
            text-align:center; font-size:0.8rem; opacity:.75; margin-bottom:10px;
        }}
        .hud-slider {{width:100%; accent-color:#38bdf8; cursor:pointer; margin-bottom:10px;}}
        .hud-btns {{display:flex; gap:8px; justify-content:center; align-items:center;}}
        .hud-btn {{
            padding:6px 16px; border:1px solid rgba(56,189,248,0.3);
            border-radius:6px; cursor:pointer; font-weight:600;
            background:rgba(56,189,248,0.08); color:#7dd3fc;
            font-size:.76rem; transition:background .15s,border-color .15s;
        }}
        .hud-btn:hover {{background:rgba(56,189,248,0.18); border-color:rgba(56,189,248,0.55);}}
        .hud-sep {{border-left:1px solid rgba(56,189,248,0.2); height:20px; margin:0 6px;}}
        .hud-select {{
            background:rgba(13,20,36,0.8); color:#7dd3fc;
            border:1px solid rgba(56,189,248,0.3); border-radius:6px;
            padding:4px 8px; font-size:.76rem; cursor:pointer; outline:none;
        }}
    </style>

    <div class="hud-wrap">
        <div class="hud-time" id="hudTime">--:--:--</div>
        <div class="hud-info" id="hudInfo">Menunggu plugin...</div>
        <input type="range" class="hud-slider" id="hudSlider"
               min="0" max="100" value="0" disabled>
        <div class="hud-btns">
            <button class="hud-btn" onclick="window._tactPlay()">▶ Play</button>
            <button class="hud-btn" onclick="window._tactPause()">⏸ Pause</button>
            <button class="hud-btn" onclick="window._tactReset()">↺ Reset</button>
            <div class="hud-sep"></div>
            <select class="hud-select" onchange="window._tactSpeed(this.value)">
                <option value="1">1×</option>
                <option value="2">2×</option>
                <option value="4">4×</option>
                <option value="8">8×</option>
            </select>
        </div>
    </div>

    <script>
    /*
     * Inline Leaflet.MovingMarker — waits for L to be defined before
     * registering the plugin, then initialises the animation immediately.
     * This avoids the "typeof L === undefined" race condition.
     */
    (function waitForLeaflet() {{
        if (typeof L === 'undefined' || !L.Marker) {{
            return setTimeout(waitForLeaflet, 60);
        }}

        // ── Register MovingMarker plugin inline (no external script src) ────
        if (!L.Marker.movingMarker) {{
            {_moving_marker_src}
        }}

        // ── Resolve the Folium map instance ─────────────────────────────────
        function getMap() {{
            let map;
            try {{ map = {map_id}; }} catch(e) {{}}
            if (map && map._leaflet_id && map.getCenter) return map;
            // Fallback: look in window globals
            for (const k of Object.keys(window)) {{
                const v = window[k];
                if (v && v._leaflet_id && typeof v.getCenter === 'function') return v;
            }}
            return null;
        }}

        function initAnimation() {{
            const map = getMap();
            if (!map) return setTimeout(initAnimation, 80);

            // ── Data ────────────────────────────────────────────────────────
            const pts     = [{waypoints_js}];
            const latlngs = pts.map(p => p.latlng);
            const baseDur = [{durations_js}];   // ms per segment
            let speedFactor = 1;

            // ── Ship icon ───────────────────────────────────────────────────
            const shipIcon = L.icon({{
                iconUrl:   'https://cdn-icons-png.flaticon.com/512/870/870082.png',
                iconSize:  [32, 32],
                iconAnchor:[16, 16]
            }});

            // ── Factory: create a fresh MovingMarker (needed for reset/speed) ──
            let pollTimer;
            function createMarker(durations) {{
                const mk = L.Marker.movingMarker(latlngs, durations, {{ autostart: false }});
                mk.setIcon(shipIcon).addTo(map);

                // Official 'end' event
                mk.on('end', () => {{
                    clearInterval(pollTimer);
                    slider.value     = 100;
                    elTime.innerText = pts[pts.length - 1].time;
                    elInfo.innerText = pts[pts.length - 1].loc + '  ·  Selesai ✓';
                }});
                return mk;
            }}

            let mk = createMarker([...baseDur]);

            // ── HUD DOM references ──────────────────────────────────────────
            const elTime = document.getElementById('hudTime');
            const elInfo = document.getElementById('hudInfo');
            const slider = document.getElementById('hudSlider');

            elTime.innerText = pts[0].time;
            elInfo.innerText = pts[0].loc;

            // ── Polling loop: pan map + update HUD (no checkpoint event in API) ──
            function startPolling() {{
                clearInterval(pollTimer);
                pollTimer = setInterval(() => {{
                    if (!mk.isRunning()) return;
                    const pos = mk.getLatLng();
                    map.panTo(pos);

                    // Find closest waypoint index for HUD label
                    let closest = 0, minDist = Infinity;
                    pts.forEach((p, i) => {{
                        const d = map.distance(pos, L.latLng(p.latlng));
                        if (d < minDist) {{ minDist = d; closest = i; }}
                    }});
                    elTime.innerText = pts[closest].time;
                    elInfo.innerText = pts[closest].loc;
                    slider.value     = (closest / (pts.length - 1)) * 100;
                }}, 250);
            }}

            // ── Controls ─────────────────────────────────────────────────────
            // start() handles both first-play and resume-after-pause (official API)
            window._tactPlay = () => {{ mk.start(); startPolling(); }};

            window._tactPause = () => {{ mk.pause(); clearInterval(pollTimer); }};

            window._tactReset = () => {{
                mk.stop(); clearInterval(pollTimer); mk.remove();
                mk = createMarker(baseDur.map(d => Math.max(50, Math.floor(d / speedFactor))));
                map.setView(latlngs[0], Math.max(map.getZoom(), 8));
                elTime.innerText = pts[0].time;
                elInfo.innerText = pts[0].loc;
                slider.value = 0;
            }};

            // Recreate with new speed (official API has no public duration setter)
            window._tactSpeed = (val) => {{
                const wasRunning = mk.isRunning();
                mk.stop(); clearInterval(pollTimer); mk.remove();
                speedFactor = Math.max(parseFloat(val) || 1, 0.1);
                mk = createMarker(baseDur.map(d => Math.max(50, Math.floor(d / speedFactor))));
                if (wasRunning) {{ mk.start(); startPolling(); }}
            }};
        }}

        initAnimation();
    }})();
    </script>
    """
    m.get_root().html.add_child(Element(hud_html))


# ---------------------------------------------------------------------------
# Map page renderer
# ---------------------------------------------------------------------------
def render_map_content():
    st.title("🗺️ Peta Posisi Kapal")
    inject_custom_css()

    if "search_select" not in st.session_state:
        st.session_state["search_select"] = None

    df = get_vessel_position()

    maint_df = active_df = pd.DataFrame()
    if not df.empty:
        df['status_lower'] = df['Status'].astype(str).str.lower()
        maint_df  = df[df['status_lower'].str.contains('maintenance|repair|mtc', na=False)]
        active_df = df[~df['status_lower'].str.contains('maintenance|repair|mtc', na=False)]

    # 1:1:1 ratio or adjust based on preference, map in center needs more space usually. Let's make it [1, 2, 1]
    tab1, tab2, tab3 = st.columns([1, 2.5, 1])

    with tab1:
        render_vessel_list_column("Active", active_df, "⚓", height=670)

    with tab2:
        # ── Search bar (full width within center column) ──────────────────────
        vessel_options = df['code_vessel'].tolist() if not df.empty else []
        current_sel    = st.session_state.get("search_select")
        sel_idx        = (vessel_options.index(current_sel) + 1) if current_sel in vessel_options else 0

        chosen = st.selectbox("🔍 Cari Kapal / ID:",
                            options=["Semua Kapal"] + vessel_options, index=sel_idx)
        st.session_state["search_select"] = chosen if chosen != "Semua Kapal" else None
        final = st.session_state["search_select"]

        center, zoom = [-1.2, 108.5], 5
        if final and not df.empty:
            row = df[df['code_vessel'] == final]
            if not row.empty:
                center = [row.iloc[0]['latitude'], row.iloc[0]['longitude']]
                zoom   = 10

        # Provide a vessel_df with only the filtered vessels
        view_df = df[df['code_vessel'] == final] if final else df
        
        # Render the enhanced bathymetric map instead of the standard markers map
        render_bathymetric_map(
            vessel_df=view_df,
            center=center,
            zoom=zoom,
            height=530
        )
        
        if final and not df.empty:
            row = df[df['code_vessel'] == final]
            if not row.empty:
                render_vessel_detail_section(row.iloc[0])

    with tab3:
        render_vessel_list_column("Maintenance", maint_df, "🛠️", height=670)




# ---------------------------------------------------------------------------
# Area Chart — daily time series with gradient fill (for environment view)
# ---------------------------------------------------------------------------
_AREA_COLORS = {
    "salinitas": ("#38bdf8", "rgba(56,189,248,0.15)"),
    "turbidity": ("#f59e0b", "rgba(245,158,11,0.15)"),
    "oxygen":    ("#22c55e", "rgba(34,197,94,0.15)"),
    "density":   ("#a78bfa", "rgba(167,139,250,0.15)"),
    "current":   ("#ef4444", "rgba(239,68,68,0.15)"),
    "tide":      ("#fb923c", "rgba(251,146,60,0.15)"),
}
_AREA_DEFAULT = ("#ef4444", "rgba(239,68,68,0.15)")


def env_area_chart(
    df: "pd.DataFrame",
    date_col: str,
    value_col: str,
    title: str = "",
    height: int = 260,
) -> "go.Figure":
    """
    Smooth area chart for a single environmental parameter.

    Aggregates df by day (mean), then renders:
      - Filled area from zero to the line
      - Solid line on top with dot markers
      - Dark transparent theme matching the design system
    """
    import plotly.graph_objects as go
    import numpy as np
    import pandas as pd

    line_color, fill_color = _AREA_COLORS.get(value_col, _AREA_DEFAULT)

    # ── Empty guard ───────────────────────────────────────────────────────────
    if df.empty or value_col not in df.columns or date_col not in df.columns:
        fig = go.Figure()
        fig.add_annotation(
            text="Tidak ada data",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(color="#475569", size=13, family="Outfit"),
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=height, margin=dict(t=36, l=0, r=0, b=0),
        )
        return fig

    # ── Aggregate daily ───────────────────────────────────────────────────────
    work = df[[date_col, value_col]].copy()
    work[date_col]  = pd.to_datetime(work[date_col], errors="coerce")
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce")
    work = work.dropna()

    daily = (
        work.groupby(work[date_col].dt.date)[value_col]
        .mean()
        .reset_index()
    )
    daily.columns = ["date", "value"]
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")

    if daily.empty:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=height,
        )
        return fig

    # ── Build figure ──────────────────────────────────────────────────────────
    fig = go.Figure()

    # Filled area
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["value"],
        mode="lines",
        fill="tozeroy",
        fillcolor=fill_color,
        line=dict(color=line_color, width=2.5, shape="spline", smoothing=1.1),
        name=value_col.capitalize(),
        hovertemplate=(
            "<b>%{x|%d %b %Y}</b><br>"
            f"{value_col.capitalize()}: <b>%{{y:.2f}}</b><extra></extra>"
        ),
    ))

    # Invisible dot markers for hover precision
    fig.add_trace(go.Scatter(
        x=daily["date"],
        y=daily["value"],
        mode="markers",
        marker=dict(color=line_color, size=5, opacity=0.7),
        showlegend=False,
        hoverinfo="skip",
    ))

    # Min / max annotations
    if len(daily) >= 2:
        vmax = daily.loc[daily["value"].idxmax()]
        vmin = daily.loc[daily["value"].idxmin()]
        for v, label, ay in [(vmax, "▲ Max", -28), (vmin, "▼ Min", 28)]:
            fig.add_annotation(
                x=v["date"], y=v["value"],
                text=f"{label}: {v['value']:.1f}",
                font=dict(color=line_color, size=9, family="Inter"),
                showarrow=True,
                arrowhead=0, arrowcolor=line_color, arrowwidth=1,
                ay=ay, ax=0,
                bgcolor="rgba(10,12,22,0.80)",
                bordercolor=line_color,
                borderwidth=1,
                borderpad=3,
            )

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family="Outfit", size=13, color="#94a3b8"),
            x=0, xanchor="left",
        ) if title else dict(text=""),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,28,0.55)",
        height=height,
        margin=dict(t=40 if title else 12, l=50, r=16, b=36),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="rgba(255,255,255,0.07)",
            tickfont=dict(color="#64748b", size=10, family="Inter"),
            tickformat="%b %d",
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(255,255,255,0.04)",
            gridwidth=1,
            showline=False,
            zeroline=False,
            tickfont=dict(color="#64748b", size=10, family="Inter"),
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(10,12,22,0.96)",
            bordercolor=line_color,
            font=dict(family="Inter", color="#f1f5f9", size=12),
        ),
    )
    return fig


def _interp_colorscale(scale, t):
    """Linearly interpolate a Plotly colorscale at position t ∈ [0,1]."""
    import re
    t = max(0.0, min(1.0, float(t)))
    for i in range(len(scale) - 1):
        t0, c0 = scale[i][0], scale[i][1]
        t1, c1 = scale[i + 1][0], scale[i + 1][1]
        if t0 <= t <= t1:
            a = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            def _p(c):
                v = [float(x) for x in re.findall(r"[\d.]+", c)]
                while len(v) < 4: v.append(1.0)
                return v
            v0, v1 = _p(c0), _p(c1)
            r  = v0[0] + a * (v1[0] - v0[0])
            g  = v0[1] + a * (v1[1] - v0[1])
            b  = v0[2] + a * (v1[2] - v0[2])
            aa = v0[3] + a * (v1[3] - v0[3])
            return f"rgba({r:.0f},{g:.0f},{b:.0f},{aa:.2f})"
    return scale[-1][1] if scale else "rgba(200,200,200,1)"


def calendar_heatmap(df, date_col, value_col, title="",
                     color_scale=None, height=None, year=None, month=None):
    """
    GitHub Contribution Graph–style calendar heatmap (full year).

    Layout  : X = week columns (left→right = time), Y = day of week (Mon top, Sun bottom)
    Visual  : Plotly Shapes (rect) → pixel-perfect cells with uniform gaps
    Events  : Invisible go.Scatter → carries YYYY-MM-DD customdata for on_select
    Colors  : cerah (low value) → pekat (high value); empty = near-black
    Labels  : Month abbreviations above grid; Mon/Wed/Fri on Y-axis
    """
    import plotly.graph_objects as go
    import pandas as pd
    import datetime

    # ── Default color scale (GitHub green tone) ───────────────────────────────
    if not color_scale:
        color_scale = [
            [0.0, "rgba(57,211,83,0.25)"],
            [0.4, "rgba(0,157,63,0.85)"],
            [1.0, "rgba(0,64,26,1.0)"],
        ]

    # ── Determine target year (month param kept for API compat, ignored here) ─
    today = datetime.date.today()
    if year is None:
        if not df.empty and date_col in df.columns:
            ts  = pd.to_datetime(df[date_col], errors="coerce").dropna()
            year = int(ts.max().year) if not ts.empty else today.year
        else:
            year = today.year

    # ── Aggregate daily means for the full year ───────────────────────────────
    daily: dict = {}
    if not df.empty and value_col in df.columns and date_col in df.columns:
        work = df[[date_col, value_col]].copy()
        work[date_col]  = pd.to_datetime(work[date_col],  errors="coerce")
        work[value_col] = pd.to_numeric(work[value_col],  errors="coerce")
        work = work.dropna()
        work = work[work[date_col].dt.year == year]
        if not work.empty:
            for d, v in work.groupby(work[date_col].dt.date)[value_col].mean().items():
                daily[d] = float(v)

    vmin = min(daily.values()) if daily else 0.0
    vmax = max(daily.values()) if daily else 1.0
    if vmin == vmax:
        vmax = vmin + 1.0

    # ── Calendar structure ────────────────────────────────────────────────────
    jan1  = datetime.date(year, 1, 1)
    dec31 = datetime.date(year, 12, 31)
    # Start from the Monday on or before Jan 1 (aligns weekday columns)
    start = jan1 - datetime.timedelta(days=jan1.weekday())

    total_days = (dec31 - start).days + 1
    n_weeks    = (total_days + 6) // 7

    # Y-position mapping: Mon(weekday=0)→y=6 (top), Sun(weekday=6)→y=0 (bottom)
    # Default Plotly: y increases upward → y=6 renders higher than y=0
    DOW_Y = {i: 6 - i for i in range(7)}

    GAP = 0.055   # fractional gap between cells (data-units)

    MONTH_SHORT = ["","Jan","Feb","Mar","Apr","Mei","Jun",
                   "Jul","Agu","Sep","Okt","Nov","Des"]
    DAY_LABELS  = {6: "Sen", 4: "Rab", 2: "Jum"}  # y-value → label (Mon/Wed/Fri)

    # ── Month-label annotations (above grid, one per month start) ────────────
    annotations = []
    for m in range(1, 13):
        first   = datetime.date(year, m, 1)
        x_col   = (first - start).days // 7
        annotations.append(dict(
            x=x_col, y=7.35,
            xref="x", yref="y",
            text=f"<b>{MONTH_SHORT[m]}</b>",
            showarrow=False,
            font=dict(size=10, color="#8b949e", family="Inter"),
            xanchor="left", yanchor="bottom",
        ))

    # ── Build shapes + scatter click/hover data ───────────────────────────────
    shapes  = []
    d_x, d_y, d_cdata, d_hover = [], [], [], []
    e_x, e_y,          e_hover = [], [],       []

    for offset in range(total_days):
        d   = start + datetime.timedelta(days=offset)
        if d > dec31:
            break

        x   = offset // 7          # week column
        dow = offset % 7           # weekday (0=Mon ... 6=Sun)
        y   = float(DOW_Y[dow])    # y: 6=Mon(top) … 0=Sun(bottom)

        x0, x1 = x - 0.5 + GAP, x + 0.5 - GAP
        y0, y1 = y - 0.5 + GAP, y + 0.5 - GAP

        if d.year != year:
            # Pre–Jan-1 padding: very faint cell, no interaction
            shapes.append(dict(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                               fillcolor="rgba(22,27,34,0.30)",
                               line_width=0, layer="below"))
            continue

        val = daily.get(d)
        if val is not None:
            t    = (val - vmin) / (vmax - vmin)
            fill = _interp_colorscale(color_scale, t)
            d_x.append(float(x)); d_y.append(y)
            d_cdata.append(d.strftime("%Y-%m-%d"))
            d_hover.append(
                f"<b>{d.strftime('%A, %d %B %Y')}</b><br>"
                f"{value_col.capitalize()}: <b>{val:.2f}</b>"
            )
        else:
            fill = "rgba(22,27,34,0.90)"    # dark cell = no data
            e_x.append(float(x)); e_y.append(y)
            e_hover.append(
                f"<b>{d.strftime('%A, %d %B %Y')}</b><br>"
                "<span style='color:#8b949e'>Tidak ada data</span>"
            )

        shapes.append(dict(type="rect", x0=x0, y0=y0, x1=x1, y1=y1,
                           fillcolor=fill, line_width=0, layer="below"))

    # ── Legend row (below grid at y = -1.1) ─────────────────────────────────
    LY = -1.1      # y-center of legend row
    LX_START = 1   # x-start for legend

    # ① No-data square
    shapes.append(dict(type="rect",
                       x0=LX_START - 0.5 + GAP, x1=LX_START + 0.5 - GAP,
                       y0=LY - 0.5 + GAP,        y1=LY + 0.5 - GAP,
                       fillcolor="rgba(22,27,34,0.90)", line_width=0, layer="below"))
    annotations.append(dict(
        x=LX_START + 0.75, y=LY,
        xref="x", yref="y",
        text="<span style='font-size:9px;color:#8b949e;font-family:Inter'>Tidak ada data</span>",
        showarrow=False, xanchor="left", yanchor="middle",
    ))

    # ② Gradient squares: Rendah → Tinggi (5 steps)
    N_STEPS     = 5
    GRAD_START  = LX_START + 6   # x offset after 'Tidak ada data' label
    annotations.append(dict(
        x=GRAD_START - 1.0, y=LY,
        xref="x", yref="y",
        text="<span style='font-size:9px;color:#8b949e;font-family:Inter'>Rendah</span>",
        showarrow=False, xanchor="right", yanchor="middle",
    ))
    for i in range(N_STEPS):
        t    = i / (N_STEPS - 1)
        fill = _interp_colorscale(color_scale, t)
        gx   = GRAD_START + i
        shapes.append(dict(type="rect",
                           x0=gx - 0.5 + GAP, x1=gx + 0.5 - GAP,
                           y0=LY - 0.5 + GAP,  y1=LY + 0.5 - GAP,
                           fillcolor=fill, line_width=0, layer="below"))
    annotations.append(dict(
        x=GRAD_START + N_STEPS - 0.25, y=LY,
        xref="x", yref="y",
        text="<span style='font-size:9px;color:#8b949e;font-family:Inter'>Tinggi</span>",
        showarrow=False, xanchor="left", yanchor="middle",
    ))

    # ── Figure ────────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Invisible hover-only for empty days
    if e_x:
        fig.add_trace(go.Scatter(
            x=e_x, y=e_y, mode="markers",
            marker=dict(size=10, opacity=0, color="rgba(0,0,0,0)"),
            hovertext=e_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        ))

    # Invisible hover+click for data days (carries customdata = date string)
    if d_x:
        fig.add_trace(go.Scatter(
            x=d_x, y=d_y, mode="markers",
            marker=dict(size=10, opacity=0, color="rgba(0,0,0,0)"),
            customdata=d_cdata,
            hovertext=d_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        ))

    # ── Title ─────────────────────────────────────────────────────────────────
    ttl = str(year)
    if title:
        ttl += f"  ·  {title}"

    fig.update_layout(
        title=dict(
            text=ttl,
            x=0, xanchor="left",
            font=dict(size=13, family="Outfit", color="#8b949e"),
            pad=dict(b=2),
        ),
        shapes=shapes,
        annotations=annotations,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,17,23,0.85)",
        autosize=True,    # ← let height auto-fit to maintain square aspect ratio
        margin=dict(t=46, l=38, r=16, b=8),
        xaxis=dict(
            range=[-0.5, n_weeks - 0.5],
            fixedrange=True,
            showgrid=False, zeroline=False, showline=False,
            showticklabels=False,
            constrain="domain",
        ),
        yaxis=dict(
            # -1.75 gives room for legend row; 7.8 gives room for month labels
            range=[-1.75, 7.8],
            fixedrange=True,
            showgrid=False, zeroline=False, showline=False,
            tickmode="array",
            tickvals=list(DAY_LABELS.keys()),
            ticktext=list(DAY_LABELS.values()),
            tickfont=dict(size=9, color="#8b949e", family="Inter"),
            # ← forces square cells: 1 y-unit = 1 x-unit in pixels
            scaleanchor="x",
            scaleratio=1,
            constrain="domain",
        ),
        clickmode="event+select",
        dragmode=False,
        hovermode="closest",
    )
    return fig


def page_heatmap(df, indikator):
    pass



    # ── Default color scale ───────────────────────────────────────────────────
    if not color_scale:
        color_scale = [
            [0.0, "rgba(235,255,245,1)"],
            [0.5, "rgba(64,196,99,1)"],
            [1.0, "rgba(21,68,37,1)"],
        ]

    # ── Target year / month ──────────────────────────────────────────────────
    if year is None or month is None:
        if not df.empty and date_col in df.columns:
            ts  = pd.to_datetime(df[date_col], errors="coerce").dropna()
            ref = ts.max() if not ts.empty else pd.Timestamp.now()
        else:
            ref = pd.Timestamp.now()
        year  = year  if year  is not None else ref.year
        month = month if month is not None else ref.month

    MONTH_ID = ["","Januari","Februari","Maret","April","Mei","Juni",
                "Juli","Agustus","September","Oktober","November","Desember"]

    # ── Aggregate daily data for this month ───────────────────────────────────
    daily: dict = {}
    if not df.empty and value_col in df.columns and date_col in df.columns:
        work = df[[date_col, value_col]].copy()
        work[date_col]  = pd.to_datetime(work[date_col],  errors="coerce")
        work[value_col] = pd.to_numeric(work[value_col],  errors="coerce")
        work = work.dropna()
        work = work[(work[date_col].dt.year == year) & (work[date_col].dt.month == month)]
        if not work.empty:
            for d, v in work.groupby(work[date_col].dt.date)[value_col].mean().items():
                daily[d] = float(v)

    vmin = min(daily.values()) if daily else 0.0
    vmax = max(daily.values()) if daily else 1.0
    if vmin == vmax:
        vmax = vmin + 1.0

    # ── Calendar structure ────────────────────────────────────────────────────
    weeks    = cal_lib.monthcalendar(year, month)   # Mon=0 … Sun=6, 0=padding
    n_weeks  = len(weeks)
    DAY_ABBR = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"]
    GAP      = 0.06   # gap between cells (in data units)

    # ── Day-name header annotations ───────────────────────────────────────────
    # We place them above the top row (y = n_weeks)
    annotations = []
    for dow, name in enumerate(DAY_ABBR):
        annotations.append(dict(
            x=dow, y=n_weeks + 0.25,
            xref="x", yref="y",
            text=f"<span style='font-size:10px;font-family:Inter;color:#64748b'><b>{name}</b></span>",
            showarrow=False,
            xanchor="center", yanchor="bottom",
        ))

    # ── Build shapes + scatter data ───────────────────────────────────────────
    shapes  = []
    d_x, d_y, d_cdata, d_hover = [], [], [], []
    e_x, e_y,          e_hover = [], [],       []

    for w_idx, week in enumerate(weeks):
        # Top week (w_idx=0) → highest y value; bottom week → y=0
        y_c = float(n_weeks - 1 - w_idx)

        for dow, day_num in enumerate(week):
            if day_num == 0:
                continue  # padding day outside this month

            x_c = float(dow)
            d   = datetime.date(year, month, day_num)
            val = daily.get(d)

            # Cell rectangle bounds
            x0, x1 = x_c - 0.5 + GAP, x_c + 0.5 - GAP
            y0, y1 = y_c - 0.5 + GAP, y_c + 0.5 - GAP

            if val is not None:
                t     = (val - vmin) / (vmax - vmin)
                fill  = _interp_colorscale(color_scale, t)
                # Decide text color: dark text on very light cells, white on dark
                txt_c = "rgba(20,28,45,0.85)" if t < 0.4 else "rgba(255,255,255,0.88)"
                d_x.append(x_c); d_y.append(y_c)
                d_cdata.append(d.strftime("%Y-%m-%d"))
                d_hover.append(
                    f"<b>{d.strftime('%A, %d %B %Y')}</b><br>"
                    f"{value_col.capitalize()}: <b>{val:.2f}</b>"
                )
            else:
                fill  = "rgba(13,16,28,0.95)"      # near-black for no-data
                txt_c = "#2d3748"
                e_x.append(x_c); e_y.append(y_c)
                e_hover.append(
                    f"<b>{d.strftime('%A, %d %B %Y')}</b><br>"
                    "<span style='color:#64748b'>Tidak ada data</span>"
                )

            # Filled rectangle — the cell visual
            shapes.append(dict(
                type="rect",
                x0=x0, y0=y0, x1=x1, y1=y1,
                fillcolor=fill,
                line_width=0,
                layer="below",
            ))
            # Day number inside cell
            annotations.append(dict(
                x=x_c, y=y_c,
                xref="x", yref="y",
                text=f"<span style='font-size:9px;font-family:Inter;font-weight:600;'>"
                     f"{day_num}</span>",
                showarrow=False,
                xanchor="center", yanchor="middle",
            ))

    # ── Figure ────────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Invisible hover-only scatter for empty days
    if e_x:
        fig.add_trace(go.Scatter(
            x=e_x, y=e_y, mode="markers",
            marker=dict(size=36, opacity=0, color="rgba(0,0,0,0)"),
            hovertext=e_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        ))

    # Invisible hover+click scatter for data days (carries customdata)
    if d_x:
        fig.add_trace(go.Scatter(
            x=d_x, y=d_y, mode="markers",
            marker=dict(size=36, opacity=0, color="rgba(0,0,0,0)"),
            customdata=d_cdata,
            hovertext=d_hover,
            hovertemplate="%{hovertext}<extra></extra>",
            showlegend=False,
        ))

    # ── Dynamic height (auto-fit to week count for square cells) ─────────────
    # Approx: header(day names) 30px + n weeks * ~52px + bottom padding
    auto_h = 40 + n_weeks * 56 + 20   # increases proportionally
    chart_h = height if height is not None else auto_h

    # ── Month + param label ────────────────────────────────────────────────────
    ttl = f"{MONTH_ID[month]} {year}"
    if title:
        ttl += f"  ·  {title}"

    fig.update_layout(
        title=dict(
            text=ttl,
            x=0, xanchor="left",
            font=dict(size=13, family="Outfit", color="#94a3b8"),
            pad=dict(b=0),
        ),
        shapes=shapes,
        annotations=annotations,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(13,16,26,0.75)",
        height=chart_h,
        margin=dict(t=46, l=6, r=6, b=8),
        xaxis=dict(
            range=[-0.5, 6.5],
            fixedrange=True,
            showgrid=False, zeroline=False, showline=False,
            showticklabels=False,
            constrain="domain",
        ),
        yaxis=dict(
            # +0.7 headroom for the day-name header annotations
            range=[-0.5, n_weeks + 0.7],
            fixedrange=True,
            showgrid=False, zeroline=False, showline=False,
            showticklabels=False,
            scaleanchor="x",   # ← forces square cells regardless of chart size!
            scaleratio=1,
            constrain="domain",
        ),
        clickmode="event+select",
        dragmode=False,
        hovermode="closest",
    )
    return fig


def page_heatmap(df, indikator):
    pass


# ---------------------------------------------------------------------------
# Task 2 — Peta Batimetri (Depth Visualization)
# ---------------------------------------------------------------------------

def render_bathymetric_map(
    vessel_df=None,
    center=None,
    zoom=10,
    height=540,
):
    """
    Folium peta batimetri pengerukan sedimentasi laut.

    Features:
      • Simulated HeatMap overlay kedalaman (kuning=dangkal → biru tua=dalam)
      • LayerControl untuk 3 layer toggle:
          – 🏖️ Titik Tumpukan Pasir (sand accumulation spots)
          – ⛵  Rute Pengerukan      (dredging route polyline)
          – 🗑️  Lokasi Pembuangan   (dumping area polygon)
      • Ikon kapal keruk (Dredger SVG) menggantikan ikon kapal standar
      • Legend kedalaman di sisi kanan bawah peta
    """
    import math

    # ── Default center (Selat Makassar / demoy) ─────────────────────────────
    if center is None:
        if vessel_df is not None and not vessel_df.empty:
            lat_col = next((c for c in ["latitude","lat"] if c in vessel_df.columns), None)
            lon_col = next((c for c in ["longitude","lon","lng"] if c in vessel_df.columns), None)
            if lat_col and lon_col:
                center = [vessel_df[lat_col].mean(), vessel_df[lon_col].mean()]
        if center is None:
            center = [-1.50, 108.80]   # default: Kalimantan coast

    clat, clon = center

    # ── Base map ─────────────────────────────────────────────────────────────
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles="CartoDB Dark Matter",
        control_scale=True,
    )

    # ── Tambah tile layer batimetri (ESRI Ocean Basemap) ─────────────────────
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
        attr="ESRI Ocean Basemap",
        name="🌊 Ocean Basemap",
        overlay=False,
        control=True,
        opacity=0.65,
    ).add_to(m)

    # ── Weather Overlay (Fase 2) ──────────────────────────────────────────────
    folium.TileLayer(
        tiles="https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=b1b15e88fa797225412429c1c50c122a",
        attr="OpenWeatherMap",
        name="🌧️ Peta Curah Hujan",
        overlay=True,
        control=True,
        show=False,
        opacity=0.5,
    ).add_to(m)
    
    folium.TileLayer(
        tiles="https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=b1b15e88fa797225412429c1c50c122a",
        attr="OpenWeatherMap",
        name="💨 Peta Angin",
        overlay=True,
        control=True,
        show=False,
        opacity=0.5,
    ).add_to(m)





    # ── Dredger vessel markers ────────────────────────────────────────────────
    if vessel_df is not None and not vessel_df.empty:
        lat_col = next((c for c in ["latitude","lat"] if c in vessel_df.columns), "latitude")
        lon_col = next((c for c in ["longitude","lon","lng"] if c in vessel_df.columns), "longitude")
        hdg_col = next((c for c in ["heading","course"] if c in vessel_df.columns), None)
        id_col  = next((c for c in ["code_vessel","vessel_id","id"] if c in vessel_df.columns), None)

        from core.services.weather import get_vessel_weather
        
        vessel_group = folium.FeatureGroup(name="⛏️ Kapal Keruk (Dredger)", show=True)
        for _, row in vessel_df.iterrows():
            try:
                lat = float(row[lat_col]); lon = float(row[lon_col])
                hdg = float(row[hdg_col]) if hdg_col else 0
                vid = str(row[id_col]) if id_col else "—"
                
                # Fetch mini weather
                w = get_vessel_weather(lat, lon)
                
                folium.Marker(
                    [lat, lon],
                    icon=create_dredger_icon(heading=hdg, fill_color="#2DD4BF", size=22),
                    tooltip=folium.Tooltip(
                        f"<div style='font-family:Outfit,sans-serif;background:#0e1824;"
                        f"color:#2DD4BF;padding:8px 12px;border-radius:8px;"
                        f"border:1px solid rgba(45,212,191,0.3);font-size:0.82rem;'>"
                        f"<b>⛏️ {vid}</b><br>Hdg: {hdg:.0f}°<hr style='margin:4px 0; border:none; border-top:1px solid #1e293b;'/>"
                        f"Cuaca: {w['icon']} {w['condition']} ({w['temperature']}°C)<br>Ombak: {w['wave_height']}m | Angin: {w['wind_speed']}kn</div>", sticky=True),
                    popup=folium.Popup(f"<b>Kapal Keruk: {vid}</b>", max_width=200),
                ).add_to(vessel_group)
            except Exception:
                continue
        vessel_group.add_to(m)

    # ── LayerControl ──────────────────────────────────────────────────────────
    folium.LayerControl(collapsed=True, position="topright").add_to(m)

    st_folium(m, height=height, width='stretch')

