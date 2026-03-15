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
        content = re.sub(r'\s+', ' ', content).strip()
        return content
    except FileNotFoundError:
        return ""

def get_status_color(status):
    """Mengembalikan kode hex warna berdasarkan status kapal."""
    import pandas as pd
    if pd.isna(status): return "#9b59b6"
    status = str(status).lower()
    if any(x in status for x in ["active", "operational", "running", "on_duty", "operating"]): return "#2ecc71"
    elif any(x in status for x in ["berthed", "anchored", "docked"]): return "#3498db"
    elif any(x in status for x in ["inactive", "idle", "off_duty", "parked"]): return "#95a5a6"
    elif any(x in status for x in ["maintenance", "repair", "mtc"]): return "#e67e22"
    elif any(x in status for x in ["warning", "alert", "slow"]): return "#f1c40f"
    elif any(x in status for x in ["emergency", "distress", "broken", "accident", "danger"]): return "#e74c3c"
    else: return "#9b59b6"

def create_google_arrow_icon(heading, fill_color, size=15):
    """Membuat ikon panah berputar."""
    width = size * 2
    height = size * 2
    svg = f"""<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><g transform="rotate({heading}, {width/2}, {height/2})"><path d="M {width/2},{0} L {width},{height} L {width/2},{height*0.75} L {0},{height} Z" fill="{fill_color}" stroke="white" stroke-width="1.5" stroke-linejoin="round"/><circle cx="{width/2}" cy="{height*0.75}" r="{width*0.05}" fill="white" opacity="0.8"/></g></svg>"""
    return folium.DivIcon(html=svg, icon_size=(width, height), icon_anchor=(width/2, height/2))

def create_circle_icon(fill_color, size=10):
    """Membuat ikon lingkaran."""
    d = size * 2
    svg = f"""<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><circle cx="{d/2}" cy="{d/2}" r="{d/2-2}" fill="{fill_color}" stroke="white" stroke-width="2"/></svg>"""
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))


def create_dredger_icon(heading=0, fill_color="#2DD4BF", size=26):
    """
    Membuat ikon SVG kapal keruk (dredger) yang berputar sesuai heading.
    Shape: badan kapal persegi + lengan crane + semburan pasir.
    """
    w = size * 2
    h = size * 2
    svg = f"""
    <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"
         style="filter:drop-shadow(0 2px 5px rgba(0,0,0,0.6));"
         xmlns="http://www.w3.org/2000/svg">
      <g transform="rotate({heading},{w/2},{h/2})">
        <!-- Hull (badan kapal) -->
        <rect x="{w*0.22}" y="{h*0.42}" width="{w*0.56}" height="{h*0.36}"
              rx="3" fill="{fill_color}" stroke="white" stroke-width="1.5"/>
        <!-- Bow (haluan runcing) -->
        <polygon points="{w*0.50},{h*0.18} {w*0.22},{h*0.42} {w*0.78},{h*0.42}"
                 fill="{fill_color}" stroke="white" stroke-width="1.5"/>
        <!-- Cabin (anjungan) -->
        <rect x="{w*0.38}" y="{h*0.50}" width="{w*0.24}" height="{h*0.16}"
              rx="2" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.4)" stroke-width="1"/>
        <!-- Crane arm -->
        <line x1="{w*0.62}" y1="{h*0.55}" x2="{w*0.82}" y2="{h*0.38}"
              stroke="#E9C46A" stroke-width="2" stroke-linecap="round"/>
        <!-- Crane bucket -->
        <circle cx="{w*0.82}" cy="{h*0.36}" r="{w*0.06}"
                fill="#D4A373" stroke="white" stroke-width="1"/>
        <!-- Suction pipe (selang) -->
        <line x1="{w*0.35}" y1="{h*0.78}" x2="{w*0.35}" y2="{h*0.92}"
              stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Bow dot -->
        <circle cx="{w*0.50}" cy="{h*0.22}" r="{w*0.04}"
                fill="white" opacity="0.9"/>
      </g>
    </svg>
    """
    return folium.DivIcon(html=svg, icon_size=(w, h), icon_anchor=(w/2, h/2))


def create_sand_marker_icon(size=14):
    """Ikon marker tumpukan pasir — lingkaran kuning bergelombang."""
    d = size * 2
    svg = f"""
    <svg width="{d}" height="{d}" viewBox="0 0 {d} {d}"
         style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));">
      <circle cx="{d/2}" cy="{d/2}" r="{d/2-2}"
              fill="#E9C46A" stroke="#D4A373" stroke-width="2" opacity="0.92"/>
      <text x="{d/2}" y="{d/2+4}" text-anchor="middle"
            font-size="{int(d*0.45)}px" fill="#090e18" font-family="Arial">⚠</text>
    </svg>
    """
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))


def create_dumping_icon(size=14):
    """Ikon marker lokasi pembuangan sedimen — segitiga oranye."""
    d = size * 2
    svg = f"""
    <svg width="{d}" height="{d}" viewBox="0 0 {d} {d}"
         style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));">
      <polygon points="{d/2},2 {d-2},{d-2} 2,{d-2}"
               fill="#F97316" stroke="white" stroke-width="1.5" opacity="0.92"/>
      <text x="{d/2}" y="{d-4}" text-anchor="middle"
            font-size="{int(d*0.40)}px" fill="white" font-family="Arial">D</text>
    </svg>
    """
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))

