import os
import re
import folium


def load_html(filename):
    """Memuat template HTML dari folder assets, dikompresi ke satu baris."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(current_dir)
        file_path   = os.path.join(project_dir, "assets", "html", filename)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = re.sub(r'\s+', ' ', content).strip()  # Fixed: was r'\\s+' which never matched
        return content
    except FileNotFoundError:
        return ""


def get_status_color(status):
    """Mengembalikan kode hex warna berdasarkan status kapal."""
    import pandas as pd
    try:
        if pd.isna(status):
            return "#9b59b6"
    except Exception:
        pass
    status = str(status).lower()
    if any(x in status for x in ["active", "operational", "running", "on_duty", "operating"]):
        return "#2ecc71"
    elif any(x in status for x in ["berthed", "anchored", "docked"]):
        return "#3498db"
    elif any(x in status for x in ["inactive", "idle", "off_duty", "parked"]):
        return "#95a5a6"
    elif any(x in status for x in ["maintenance", "repair", "mtc"]):
        return "#e67e22"
    elif any(x in status for x in ["warning", "alert", "slow"]):
        return "#f1c40f"
    elif any(x in status for x in ["emergency", "distress", "broken", "accident", "danger"]):
        return "#e74c3c"
    return "#9b59b6"


def create_google_arrow_icon(heading, fill_color, size=15):
    """Membuat ikon panah berputar."""
    width = size * 2
    height = size * 2
    svg = """<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><g transform="rotate({rot}, {w2}, {h2})"><path d="M {w2},0 L {w},{h} L {w2},{h75} L 0,{h} Z" fill="{fc}" stroke="white" stroke-width="1.5" stroke-linejoin="round"/><circle cx="{w2}" cy="{h75}" r="{r}" fill="white" opacity="0.8"/></g></svg>"""
    svg = svg.format(w=width, h=height, rot=heading, w2=width/2, h2=height/2,
                     h75=height*0.75, fc=fill_color, r=width*0.05)
    return folium.DivIcon(html=svg, icon_size=(width, height), icon_anchor=(width/2, height/2))


def create_circle_icon(fill_color, size=10):
    """Membuat ikon lingkaran."""
    d = size * 2
    svg = """<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><circle cx="{d2}" cy="{d2}" r="{r}" fill="{fc}" stroke="white" stroke-width="2"/></svg>"""
    svg = svg.format(d=d, d2=d/2, r=d/2-2, fc=fill_color)
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))


def create_dredger_icon(heading=0, fill_color="#2DD4BF", size=26):
    """Membuat ikon SVG kapal keruk (dredger) yang berputar sesuai heading."""
    w = size * 2
    h = size * 2
    svg = """<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="filter:drop-shadow(0 2px 5px rgba(0,0,0,0.6));" xmlns="http://www.w3.org/2000/svg"><g transform="rotate({rot},{w2},{h2})"><rect x="{w22}" y="{h42}" width="{w56}" height="{h36}" rx="3" fill="{fc}" stroke="white" stroke-width="1.5"/><polygon points="{w50},{h18} {w22},{h42} {w78},{h42}" fill="{fc}" stroke="white" stroke-width="1.5"/><rect x="{w38}" y="{h50}" width="{w24}" height="{h16}" rx="2" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.4)" stroke-width="1"/><line x1="{w62}" y1="{h55}" x2="{w82}" y2="{h38}" stroke="#E9C46A" stroke-width="2" stroke-linecap="round"/><circle cx="{w82}" cy="{h36}" r="{w06}" fill="#D4A373" stroke="white" stroke-width="1"/><line x1="{w35}" y1="{h78}" x2="{w35}" y2="{h92}" stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/><circle cx="{w50}" cy="{h22}" r="{w04}" fill="white" opacity="0.9"/></g></svg>"""
    svg = svg.format(w=w, h=h, rot=heading, w2=w/2, h2=h/2, fc=fill_color,
                     w22=w*0.22, h42=h*0.42, w56=w*0.56, h36=h*0.36,
                     w50=w*0.5, h18=h*0.18, w78=w*0.78, w38=w*0.38,
                     h50=h*0.50, w24=w*0.24, h16=h*0.16, w62=w*0.62,
                     h55=h*0.55, w82=w*0.82, w06=w*0.06, w35=w*0.35,
                     h78=h*0.78, h92=h*0.92, h22=h*0.22, w04=w*0.04)
    return folium.DivIcon(html=svg, icon_size=(w, h), icon_anchor=(w/2, h/2))


def create_sand_marker_icon(size=14):
    """Ikon marker tumpukan pasir."""
    d = size * 2
    svg = """<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));"><circle cx="{d2}" cy="{d2}" r="{r}" fill="#E9C46A" stroke="#D4A373" stroke-width="2" opacity="0.92"/><text x="{d2}" y="{y}" text-anchor="middle" font-size="{fs}px" fill="#090e18" font-family="Arial">&#9888;</text></svg>"""
    svg = svg.format(d=d, d2=d/2, r=d/2-2, y=d/2+4, fs=int(d*0.45))
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))


def create_dumping_icon(size=14):
    """Ikon marker lokasi pembuangan sedimen."""
    d = size * 2
    svg = """<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));"><polygon points="{d2},2 {d_2},{d_2} 2,{d_2}" fill="#F97316" stroke="white" stroke-width="1.5" opacity="0.92"/><text x="{d2}" y="{d_4}" text-anchor="middle" font-size="{fs}px" fill="white" font-family="Arial">D</text></svg>"""
    svg = svg.format(d=d, d2=d/2, d_2=d-2, d_4=d-4, fs=int(d*0.4))
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))


def _safe_val(val):
    """Return 0 if val is None or NaN, otherwise return val as-is."""
    import pandas as pd
    try:
        if val is None or pd.isna(val):
            return 0
    except Exception:
        pass
    return val


def render_beautiful_table(df, col_config=None):
    """
    Render a sleek custom HTML table to replace standard st.dataframe.

    Args:
        df          : Pandas DataFrame
        col_config  : dict  {
            "ColName": {
                "type"         : "text" | "progress" | "badge",
                "max_val"      : float   (progress only),
                "format"       : "{:.1f}" (text/progress),
                "default_color": "#hex"  (progress fallback bar colour),
                "color_key"    : "OtherCol" (progress: read colour from another col),
                "color_map"    : {"val": "#hex"},
                "align"        : "left" | "right" | "center",
                "width"        : "120px",
            }
        }
    """
    import streamlit as st

    if df is None or df.empty:
        st.markdown(
            "<div style='padding:15px;color:#8ba3c0;font-family:Inter,sans-serif;'>Data kosong</div>",
            unsafe_allow_html=True,
        )
        return

    col_config = col_config or {}
    parts = []

    # ── Wrapper + table open ──────────────────────────────────────────────────
    parts.append(
        '<div style="background:rgba(15,23,42,0.45);border:1px solid rgba(255,255,255,0.06);'
        'border-radius:12px;overflow:hidden;margin-bottom:15px;width:100%;'
        'box-shadow:0 4px 20px rgba(0,0,0,0.15);">'
        '<table style="width:100%;border-collapse:collapse;font-family:\'Inter\',sans-serif;">'
        '<thead>'
        '<tr style="border-bottom:1px solid rgba(255,255,255,0.06);color:#94a3b8;'
        'font-size:0.78rem;text-transform:uppercase;letter-spacing:0.05em;'
        'background:rgba(0,0,0,0.25);">'
    )

    # ── Header row ────────────────────────────────────────────────────────────
    for col in df.columns:
        cfg = col_config.get(col, {})
        align = cfg.get("align", "left")
        w_style = "width:{};".format(cfg["width"]) if "width" in cfg else ""
        parts.append(
            '<th style="padding:11px 16px;font-weight:600;text-align:{};{}">{}</th>'.format(
                align, w_style, col
            )
        )

    parts.append('</tr></thead><tbody>')

    # ── Data rows ─────────────────────────────────────────────────────────────
    hover_on  = 'onmouseover="this.style.background=\'rgba(255,255,255,0.025)\'"'
    hover_off = 'onmouseout="this.style.background=\'transparent\'"'

    for _, row in df.iterrows():
        parts.append(
            '<tr style="border-bottom:1px solid rgba(255,255,255,0.025);transition:background 0.18s;" {} {}>'.format(
                hover_on, hover_off
            )
        )

        for col in df.columns:
            raw_val = _safe_val(row[col])
            cfg     = col_config.get(col, {})
            c_type  = cfg.get("type", "text")
            align   = cfg.get("align", "left")

            # ── Progress bar cell ─────────────────────────────────────────
            if c_type == "progress":
                max_v = cfg.get("max_val", 100) or 100
                try:
                    num_val = float(raw_val)
                except (TypeError, ValueError):
                    num_val = 0.0

                pct = min(100.0, max(0.0, (num_val / max_v) * 100))

                bar_color = cfg.get("default_color", "#38bdf8")
                color_map = cfg.get("color_map", {})
                ck_col    = cfg.get("color_key")
                if ck_col and ck_col in df.columns:
                    ck_val    = _safe_val(row[ck_col])
                    bar_color = color_map.get(str(ck_val), bar_color)

                fmt     = cfg.get("format", "{}")
                str_val = fmt.format(num_val) if fmt != "{}" else str(int(num_val) if num_val == int(num_val) else num_val)

                parts.append(
                    '<td style="padding:10px 16px;">'
                    '<div style="display:flex;align-items:center;gap:10px;">'
                    '<div style="flex:1;min-width:40px;height:6px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
                    '<div style="width:{pct}%;height:100%;background:{bc};border-radius:99px;box-shadow:0 0 6px {bc}60;transition:width 0.4s ease;"></div>'
                    '</div>'
                    '<span style="color:#f1f5f9;font-size:0.82rem;font-weight:600;min-width:18px;text-align:right;font-family:\'Outfit\',sans-serif;">{sv}</span>'
                    '</div></td>'.format(pct=round(pct, 1), bc=bar_color, sv=str_val)
                )

            # ── Badge cell ────────────────────────────────────────────────
            elif c_type == "badge":
                color_map = cfg.get("color_map", {})
                b_color   = color_map.get(str(raw_val), "#64748b")
                parts.append(
                    '<td style="padding:10px 16px;text-align:{a};">'
                    '<span style="background:{bc}18;color:{bc};border:1px solid {bc}35;'
                    'padding:3px 10px;border-radius:99px;font-size:0.73rem;font-weight:700;'
                    'white-space:nowrap;letter-spacing:0.03em;">{v}</span>'
                    '</td>'.format(a=align, bc=b_color, v=str(raw_val))
                )

            # ── Plain text cell ───────────────────────────────────────────
            else:
                fmt = cfg.get("format", "{}")
                try:
                    str_val = fmt.format(raw_val)
                except (TypeError, ValueError):
                    str_val = str(raw_val)
                parts.append(
                    '<td style="padding:10px 16px;color:#cbd5e1;font-size:0.84rem;'
                    'font-weight:400;text-align:{a};">{sv}</td>'.format(a=align, sv=str_val)
                )

        parts.append('</tr>')

    parts.append('</tbody></table></div>')

    st.markdown("".join(parts), unsafe_allow_html=True)
