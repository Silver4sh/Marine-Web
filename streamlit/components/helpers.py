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
