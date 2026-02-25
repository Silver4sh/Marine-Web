"""
views/environment.py
====================
UI layer untuk halaman Environment (Lingkungan).

Tanggung jawab:
  - Merender heatmap kualitas air, chart oseanografi, dan grid buoy
  - Menampilkan detail buoy via @st.dialog
  - TIDAK ada logika bisnis — hanya presentasi data
"""
import streamlit as st
import pandas as pd
import altair as alt

from core import get_data_water, page_heatmap, load_html
from core.database import get_buoy_fleet, get_buoy_history
from core.ai_analyst import MarineAIAnalyst


# ---------------------------------------------------------------------------
# Chart helpers (private)
# ---------------------------------------------------------------------------

def _line_chart(df: pd.DataFrame, x_col: str, y_col: str,
                color_col: str, title: str | None = None) -> None:
    """Merender line chart interaktif dengan Altair."""
    if df.empty or y_col not in df.columns:
        st.info("Tidak ada data untuk ditampilkan.")
        return

    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X(x_col, title="Waktu"),
            y=alt.Y(y_col, title=""),
            color=alt.Color(color_col, legend=None),
            tooltip=[x_col, y_col, color_col],
        )
        .properties(height=300, **({"title": title} if title else {}))
        .interactive()
    )
    st.altair_chart(chart, width='stretch')


def _sparkline(df: pd.DataFrame, y_col: str, title: str,
               color: str = "#0ea5e9") -> None:
    """Merender area sparkline sederhana."""
    if df.empty or y_col not in df.columns:
        return

    chart = (
        alt.Chart(df)
        .mark_area(
            line={"color": color},
            color=alt.Gradient(
                gradient="linear",
                stops=[
                    alt.GradientStop(color=color,   offset=0),
                    alt.GradientStop(color="white", offset=1),
                ],
                x1=1, x2=1, y1=1, y2=0,
            ),
        )
        .encode(
            x=alt.X("created_at", axis=alt.Axis(labels=False, grid=False, title="")),
            y=alt.Y(y_col,        axis=alt.Axis(labels=True,  grid=True,  title="")),
            tooltip=["created_at", y_col],
        )
        .properties(title=title, height=150)
    )
    st.altair_chart(chart, width='stretch')


# ---------------------------------------------------------------------------
# Buoy status styling
# ---------------------------------------------------------------------------

_BUOY_STYLES = {
    "Active": {
        "color":  "#22c55e",
        "bg":     "linear-gradient(145deg,rgba(34,197,94,0.1) 0%,rgba(15,23,42,0.6) 100%)",
        "border": "rgba(34,197,94,0.3)",
    },
    "Maintenance": {
        "color":  "#f59e0b",
        "bg":     "linear-gradient(145deg,rgba(245,158,11,0.15) 0%,rgba(15,23,42,0.6) 100%)",
        "border": "rgba(245,158,11,0.3)",
    },
    "_default": {
        "color":  "#94a3b8",
        "bg":     "linear-gradient(145deg,rgba(148,163,184,0.1) 0%,rgba(15,23,42,0.6) 100%)",
        "border": "rgba(148,163,184,0.2)",
    },
}


def _buoy_style(status: str) -> dict:
    return _BUOY_STYLES.get(status, _BUOY_STYLES["_default"])


# ---------------------------------------------------------------------------
# Heatmap section
# ---------------------------------------------------------------------------

def _prepare_oceanography_df(df: pd.DataFrame) -> pd.DataFrame:
    """Hitung rata-rata harian arus dan pasang surut lintas semua buoy."""
    if df.empty or 'latest_timestamp' not in df.columns:
        return pd.DataFrame()

    chart_df = df.copy()
    chart_df['date']    = chart_df['latest_timestamp'].dt.date
    chart_df['current'] = pd.to_numeric(chart_df['current'], errors='coerce')
    chart_df['tide']    = pd.to_numeric(chart_df['tide'],    errors='coerce')

    chart_df = (
        chart_df.groupby('date')[['current', 'tide']]
        .mean()
        .reset_index()
    )
    chart_df['id_buoy']          = 'Rata-rata Wilayah'
    chart_df['latest_timestamp'] = pd.to_datetime(chart_df['date'])
    return chart_df.sort_values('latest_timestamp')


def render_environ_heatmap() -> None:
    """Tab 1: Heatmap parameter lingkungan laut."""
    st.markdown("## 🔥 Enviro Heatmap")
    df = get_data_water()

    # Tampilkan pesan jika data kosong (DB tidak bisa diakses atau tabel kosong)
    if df.empty:
        st.warning("⚠️ Data sensor buoy tidak tersedia. Periksa koneksi database atau pastikan tabel `buoy_sensor_histories` memiliki data.")
        return

    # --- AI Analysis ---
    anomaly_df = (
        df[df['salinitas'] > 40]
        if 'salinitas' in df.columns
        else pd.DataFrame()
    )
    ai_env = MarineAIAnalyst.analyze_environment(anomaly_df)

    insights = ai_env.get('insights', [])
    if insights:
        with st.expander("🤖 AI Eco-Watch", expanded=True):
            for insight in insights:
                itype = insight.get('type', 'info')
                text  = f"**{insight['title']}**\n\n{insight['desc']}"
                if itype == 'critical':
                    st.error(text)
                elif itype == 'warning':
                    st.warning(text)
                elif itype == 'positive':
                    st.success(text)
                else:
                    st.info(text)

    # --- Filter 7 hari terakhir ---
    if 'latest_timestamp' in df.columns:
        df['latest_timestamp'] = pd.to_datetime(df['latest_timestamp'], errors='coerce')
        df = df.dropna(subset=['latest_timestamp'])
        if not df.empty:
            max_date = df['latest_timestamp'].max()
            df = df[df['latest_timestamp'] >= max_date - pd.Timedelta(days=7)]

    if df.empty:
        st.info("Tidak ada data dalam 7 hari terakhir.")
        return

    cat = st.radio("Pilih Kategori", ["Kualitas Air", "Oseanografi"], horizontal=True)

    if cat == "Kualitas Air":
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Salinitas**")
            page_heatmap(df, "salinitas")
        with c2:
            st.write("**Kekeruhan**")
            page_heatmap(df, "turbidity")
        st.write("**Oksigen**")
        page_heatmap(df, "oxygen")

    else:  # Oseanografi
        chart_df = _prepare_oceanography_df(df)
        if chart_df.empty:
            st.info("Data oseanografi tidak cukup untuk ditampilkan.")
            return
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Rerata Arus")
            _line_chart(chart_df, 'latest_timestamp', 'current', 'id_buoy')
        with c2:
            st.subheader("Rerata Pasang Surut")
            _line_chart(chart_df, 'latest_timestamp', 'tide', 'id_buoy')

        st.markdown("### Densitas")
        page_heatmap(df, "density")


# ---------------------------------------------------------------------------
# Buoy detail dialog
# ---------------------------------------------------------------------------

@st.dialog("Detail Buoy", width="large")
def view_buoy_detail(b_id: str, name: str) -> None:
    """Dialog riwayat sensor buoy."""
    st.write(f"### {name}")
    st.write(f"**ID Buoy:** {b_id}")

    hist_df = get_buoy_history(b_id)
    if hist_df.empty:
        st.warning("Belum ada data historis.")
        return

    hist_df['created_at'] = pd.to_datetime(hist_df['created_at'])
    min_date = hist_df['created_at'].min().date()
    max_date = hist_df['created_at'].max().date()

    st.markdown("#### Filter Tanggal")
    d = st.date_input("Pilih Rentang Tanggal", [min_date, max_date],
                      min_value=min_date, max_value=max_date)

    filtered_df = hist_df.copy()
    if isinstance(d, (list, tuple)) and len(d) == 2:
        start = pd.to_datetime(d[0])
        end   = pd.to_datetime(d[1]) + pd.Timedelta(days=1)
        filtered_df = hist_df[
            (hist_df['created_at'] >= start) &
            (hist_df['created_at'] <  end)
        ]

    if filtered_df.empty:
        st.info("Tidak ada data dalam rentang tanggal yang dipilih.")
        return

    st.divider()
    st.subheader("📈 Grafik Detail")

    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)
    with c1: st.caption("Salinitas");  _line_chart(filtered_df, 'created_at', 'salinitas', 'id_buoy')
    with c2: st.caption("Kekeruhan"); _line_chart(filtered_df, 'created_at', 'turbidity', 'id_buoy')
    with c3: st.caption("Oksigen");   _line_chart(filtered_df, 'created_at', 'oxygen',    'id_buoy')
    with c4: st.caption("Densitas");  _line_chart(filtered_df, 'created_at', 'density',   'id_buoy')

    st.divider()
    st.subheader("📄 Data Mentah")
    st.dataframe(filtered_df, width='stretch')


# ---------------------------------------------------------------------------
# Buoy monitoring grid
# ---------------------------------------------------------------------------

def render_buoy_monitoring() -> None:
    """Tab 2: Grid status buoy + tombol detail."""
    st.markdown("## 📡 Pemantauan Buoy")

    buoys_df = get_buoy_fleet()
    if buoys_df.empty:
        st.info("Belum ada data buoy yang aktif.")
        return

    total  = len(buoys_df)
    active = int((buoys_df['status'] == 'Active').sum())
    maint  = total - active

    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Buoy",      total)
    with c2: st.metric("Buoy Aktif",      active)
    with c3: st.metric("Dalam Perawatan", maint)

    st.markdown("### Daftar Buoy")

    html_tpl    = load_html("buoy_card.html")
    cols_per_row = 4

    for chunk_start in range(0, total, cols_per_row):
        chunk = buoys_df.iloc[chunk_start : chunk_start + cols_per_row]
        cols  = st.columns(cols_per_row)

        for col, (_, buoy) in zip(cols, chunk.iterrows()):
            with col:
                b_id      = buoy['code_buoy']
                loc       = buoy.get('location') or 'Lokasi ?'
                status    = buoy.get('status', '')
                batt      = buoy.get('battery', '-')
                last_up   = buoy.get('last_update')
                fmt_time  = last_up.strftime("%d %b %H:%M") if pd.notnull(last_up) else "-"
                style     = _buoy_style(status)

                if html_tpl:
                    card = (
                        html_tpl
                        .replace("{b_id}",         str(b_id))
                        .replace("{loc}",           str(loc))
                        .replace("{status}",        str(status))
                        .replace("{status_color}",  style['color'])
                        .replace("{bg_gradient}",   style['bg'])
                        .replace("{border_color}",  style['border'])
                        .replace("{batt}",          str(batt))
                        .replace("{fmt_update}",    fmt_time)
                    )
                    st.markdown(card, unsafe_allow_html=True)
                else:
                    st.error("Template buoy_card.html tidak ditemukan.")

                if st.button("Detail 🔍", key=f"btn_buoy_{b_id}", width='stretch'):
                    view_buoy_detail(b_id, f"Buoy {b_id} — {loc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def render_environment_page() -> None:
    """Entry point halaman Lingkungan — dipanggil dari main.py."""
    st.markdown("# 🌊 Enviro Control")
    tab1, tab2 = st.tabs(["🔥 Grafik Heatmap", "📡 Pemantauan Buoy"])
    with tab1:
        render_environ_heatmap()
    with tab2:
        render_buoy_monitoring()
