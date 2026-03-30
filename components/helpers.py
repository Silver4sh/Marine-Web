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
        content = re.sub(r'\\s+', ' ', content).strip()
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
    svg = """<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><g transform="rotate({rot}, {w2}, {h2})"><path d="M {w2},0 L {w},{h} L {w2},{h75} L 0,{h} Z" fill="{fc}" stroke="white" stroke-width="1.5" stroke-linejoin="round"/><circle cx="{w2}" cy="{h75}" r="{r}" fill="white" opacity="0.8"/></g></svg>"""
    svg = svg.format(w=width, h=height, rot=heading, w2=width/2, h2=height/2, h75=height*0.75, fc=fill_color, r=width*0.05)
    return folium.DivIcon(html=svg, icon_size=(width, height), icon_anchor=(width/2, height/2))

def create_circle_icon(fill_color, size=10):
    """Membuat ikon lingkaran."""
    d = size * 2
    svg = """<svg width="{d}" height="{d}" viewBox="0 0 {d} {d}" style="filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.5));"><circle cx="{d2}" cy="{d2}" r="{r}" fill="{fc}" stroke="white" stroke-width="2"/></svg>"""
    svg = svg.format(d=d, d2=d/2, r=d/2-2, fc=fill_color)
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))

def create_dredger_icon(heading=0, fill_color="#2DD4BF", size=26):
    """
    Membuat ikon SVG kapal keruk (dredger) yang berputar sesuai heading.
    Shape: badan kapal persegi + lengan crane + semburan pasir.
    """
    w = size * 2
    h = size * 2
    svg = """
    <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"
         style="filter:drop-shadow(0 2px 5px rgba(0,0,0,0.6));"
         xmlns="http://www.w3.org/2000/svg">
      <g transform="rotate({rot},{w2},{h2})">
        <rect x="{w22}" y="{h42}" width="{w56}" height="{h36}"
              rx="3" fill="{fc}" stroke="white" stroke-width="1.5"/>
        <polygon points="{w50},{h18} {w22},{h42} {w78},{h42}"
                 fill="{fc}" stroke="white" stroke-width="1.5"/>
        <rect x="{w38}" y="{h50}" width="{w24}" height="{h16}"
              rx="2" fill="rgba(255,255,255,0.25)" stroke="rgba(255,255,255,0.4)" stroke-width="1"/>
        <line x1="{w62}" y1="{h55}" x2="{w82}" y2="{h38}"
              stroke="#E9C46A" stroke-width="2" stroke-linecap="round"/>
        <circle cx="{w82}" cy="{h36}" r="{w06}"
                fill="#D4A373" stroke="white" stroke-width="1"/>
        <line x1="{w35}" y1="{h78}" x2="{w35}" y2="{h92}"
              stroke="#38BDF8" stroke-width="2.5" stroke-linecap="round"/>
        <circle cx="{w50}" cy="{h22}" r="{w04}"
                fill="white" opacity="0.9"/>
      </g>
    </svg>
    """
    svg = svg.format(w=w, h=h, rot=heading, w2=w/2, h2=h/2, fc=fill_color, w22=w*0.22, h42=h*0.42, w56=w*0.56, h36=h*0.36, w50=w*0.5, h18=h*0.18, w78=w*0.78, w38=w*0.38, h50=h*0.50, w24=w*0.24, h16=h*0.16, w62=w*0.62, h55=h*0.55, w82=w*0.82, h38=h*0.38, w06=w*0.06, w35=w*0.35, h78=h*0.78, h92=h*0.92, h22=h*0.22, w04=w*0.04)
    return folium.DivIcon(html=svg, icon_size=(w, h), icon_anchor=(w/2, h/2))

def create_sand_marker_icon(size=14):
    """Ikon marker tumpukan pasir — lingkaran kuning bergelombang."""
    d = size * 2
    svg = """
    <svg width="{d}" height="{d}" viewBox="0 0 {d} {d}"
         style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));">
      <circle cx="{d2}" cy="{d2}" r="{r}"
              fill="#E9C46A" stroke="#D4A373" stroke-width="2" opacity="0.92"/>
      <text x="{d2}" y="{y}" text-anchor="middle"
            font-size="{fs}px" fill="#090e18" font-family="Arial">⚠</text>
    </svg>
    """
    svg = svg.format(d=d, d2=d/2, r=d/2-2, y=d/2+4, fs=int(d*0.45))
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))

def create_dumping_icon(size=14):
    """Ikon marker lokasi pembuangan sedimen — segitiga oranye."""
    d = size * 2
    svg = """
    <svg width="{d}" height="{d}" viewBox="0 0 {d} {d}"
         style="filter:drop-shadow(0 1px 3px rgba(0,0,0,0.5));">
      <polygon points="{d2},2 {d_2},{d_2} 2,{d_2}"
               fill="#F97316" stroke="white" stroke-width="1.5" opacity="0.92"/>
      <text x="{d2}" y="{d_4}" text-anchor="middle"
            font-size="{fs}px" fill="white" font-family="Arial">D</text>
    </svg>
    """
    svg = svg.format(d=d, d2=d/2, d_2=d-2, d_4=d-4, fs=int(d*0.4))
    return folium.DivIcon(html=svg, icon_size=(d, d), icon_anchor=(d/2, d/2))

def render_beautiful_table(df, col_config=None):
    """
    Render a sleek custom HTML table to replace standard st.dataframe.
    df: Pandas dataframe.
    col_config: dict specifying how to render columns.
      Format: { "Col_Name": { "type": "progress", "max_val": 100, "color_map": {"Valid": "green"}, "width": "150px" }, ... }
    """
    if df.empty:
        import streamlit as st
        st.markdown("<div style='padding: 15px; color: #8ba3c0;'>Data kosong</div>", unsafe_allow_html=True)
        return
    
    col_config = col_config or {}
    
    html = '''
    <div style="background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05); border-radius: 12px; overflow: hidden; margin-bottom: 15px; width: 100%; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
        <table style="width: 100%; border-collapse: collapse; font-family: 'Inter', sans-serif;">
            <thead>
                <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); color: #94a3b8; font-size: 0.8rem; text-align: left; background: rgba(0,0,0,0.2);">
    '''
    
    for col in df.columns:
        cfg = col_config.get(col, {})
        width_style = "width: {};".format(cfg['width']) if "width" in cfg else ""
        align = cfg.get("align", "left")
        th_html = '<th style="padding: 12px 16px; font-weight: 600; text-align: {align}; {w}">{c}</th>'
        html += th_html.format(align=align, w=width_style, c=col)
        
    html += '</tr></thead><tbody>'
    
    for _, row in df.iterrows():
        html += '<tr style="border-bottom: 1px solid rgba(255,255,255,0.02); transition: background 0.2s;" onmouseover="this.style.background=\\\'rgba(255,255,255,0.02)\\\'" onmouseout="this.style.background=\\\'transparent\\\'">\\n'
        for col in df.columns:
            val = row[col]
            import pandas as pd
            if pd.isna(val) or val is None:
                val = 0
                
            cfg = col_config.get(col, {})
            c_type = cfg.get("type", "text")
            align = cfg.get("align", "left")
            
            if c_type == "progress":
                max_v = cfg.get("max_val", 100)
                try: 
                    num_val = float(val) if val is not None else 0.0
                except: 
                    num_val = 0.0
                    
                pct = (num_val / max_v * 100) if max_v > 0 else 0
                pct = min(100, max(0, pct))
                
                color_map = cfg.get("color_map", {})
                bar_color = cfg.get("default_color", "#38bdf8")
                
                color_key_col = cfg.get("color_key")
                if color_key_col and color_key_col in df.columns:
                    key_val = str(row[color_key_col])
                    bar_color = color_map.get(key_val, bar_color)
                
                fmt = cfg.get("format", "{}")
                str_val = fmt.format(val) if val is not None else ""
                
                td_html = '''
                    <td style="padding: 10px 16px;">
                        <div style="display: flex; align-items: center; gap: 12px; justify-content: {a};">
                            <div style="flex-grow: 1; min-width: 50px; height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                                <div style="width: {p}%; height: 100%; background: {bc}; border-radius: 10px; box-shadow: 0 0 5px {bc}80;"></div>
                            </div>
                            <span style="color: #f1f5f9; font-size: 0.85rem; font-weight: 600; font-family: \\'Outfit\\', sans-serif; min-width: 20px; text-align: right;">{sv}</span>
                        </div>
                    </td>
                '''
                html += td_html.replace('{a}', str(align)).replace('{p}', str(pct)).replace('{bc}', str(bar_color)).replace('{sv}', str(str_val))
                
            elif c_type == "badge":
                color_map = cfg.get("color_map", {})
                b_color = color_map.get(str(val), "#64748b")
                
                td_html = '''
                    <td style="padding: 10px 16px; text-align: {a};">
                        <span style="background: {bc}15; color: {bc}; border: 1px solid {bc}30; padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; white-space: nowrap;">
                            {v}
                        </span>
                    </td>
                '''
                html += td_html.replace('{a}', str(align)).replace('{bc}', str(b_color)).replace('{v}', str(val))
                
            else:
                fmt = cfg.get("format", "{}")
                str_val = fmt.format(val) if val is not None else ""
                td_html = '<td style="padding: 10px 16px; color: #e2eff8; font-size: 0.85rem; font-weight: 500; text-align: {a};">{sv}</td>\\n'
                html += td_html.replace('{a}', str(align)).replace('{sv}', str(str_val))
                
        html += '</tr>\\n'
        
    html += '</tbody></table></div>'
    
    clean_html = "\\n".join([line.strip() for line in html.split('\\n')])
    
    import streamlit as st
    st.markdown(clean_html, unsafe_allow_html=True)
