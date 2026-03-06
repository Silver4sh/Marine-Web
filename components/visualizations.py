from components.helpers import get_status_color, create_google_arrow_icon
from components.cards import render_vessel_list_column, render_vessel_detail_section
from db.repositories.fleet_repo import get_vessel_position, get_path_vessel
from config.settings import inject_custom_css
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

    # ── Search bar (full width) ─────────────────────────────────────────────
    vessel_options = df['code_vessel'].tolist() if not df.empty else []
    current_sel    = st.session_state.get("search_select")
    sel_idx        = (vessel_options.index(current_sel) + 1) if current_sel in vessel_options else 0

    chosen = st.selectbox("🔍 Cari Kapal / ID:",
                          options=["Semua Kapal"] + vessel_options, index=sel_idx)
    st.session_state["search_select"] = chosen if chosen != "Semua Kapal" else None
    final = st.session_state["search_select"]

    # ── Map (wide) + Vessel Detail (narrow) ────────────────────────────────
    c_map, c_detail = st.columns([4, 1])

    with c_map:
        center, zoom = [-1.2, 108.5], 5
        if final and not df.empty:
            row = df[df['code_vessel'] == final]
            if not row.empty:
                center = [row.iloc[0]['latitude'], row.iloc[0]['longitude']]
                zoom   = 10

        m       = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB Dark Matter")
        cluster = MarkerCluster().add_to(m)

        view_df = df[df['code_vessel'] == final] if final else df
        for _, row in view_df.iterrows():
            try:
                vid   = row.get('code_vessel')
                color = get_status_color(row.get('Status'))
                folium.Marker(
                    [row['latitude'], row['longitude']],
                    icon=create_google_arrow_icon(row.get('heading', 0), color),
                    popup=f"<b>{vid}</b><br>{row.get('Status')}"
                ).add_to(cluster)

                if vid == final:
                    add_history_path_to_map(m, get_path_vessel(vid), color, vid, show_timelapse=True)
            except Exception:
                continue

        st_folium(m, height=620, use_container_width=true)

    with c_detail:
        if final and not df.empty:
            row = df[df['code_vessel'] == final]
            if not row.empty:
                render_vessel_detail_section(row.iloc[0])
        else:
            st.info("Pilih kapal untuk melihat detail.", icon="⬅️")

    # ── Vessel Lists (tabs below map) ───────────────────────────────────────
    st.divider()
    tab_active, tab_maint = st.tabs([
        f"⚓ Armada Aktif ({len(active_df)})",
        f"🛠️ Dalam Maintenance ({len(maint_df)})"
    ])
    with tab_active:
        render_vessel_list_column("Active", active_df, "⚓", height=320)
    with tab_maint:
        render_vessel_list_column("Maintenance", maint_df, "🛠️", height=320)



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


# Keep backward compat alias used by environment.py
def calendar_heatmap(df, date_col, value_col, title="", color_scale=None, height=260):
    """Alias → area chart (heatmap replaced)."""
    return env_area_chart(df, date_col, value_col, title=title, height=height)


def page_heatmap(df, indikator):
    """Legacy wrapper — kept so existing calls don't break."""
    pass



