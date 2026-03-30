"""core/views/client_portal.py — Safe Self-Service Portal for Clients"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta


def _demo_client_data(client_username: str) -> dict:
    today = date.today()
    return {
        "company_name": f"PT Mitra ({client_username})",
        "active_shipments": pd.DataFrame([
            {"id": "SHP-101", "vessel": "KM Nusantara Jaya", "origin": "Surabaya", "dest": "Makassar",
             "status": "Underway", "eta": str(today + timedelta(days=1)), "cargo": "20x Kontainer"}
        ]),
        "history": pd.DataFrame([
            {"id": "SHP-098", "vessel": "KM Bahari Indah", "origin": "Jakarta", "dest": "Surabaya",
             "status": "Completed", "date": str(today - timedelta(days=14)), "cargo": "15x Kontainer"}
        ]),
        "notifications": [
            {"title": "Peringatan Cuaca (Delay)", "message": "ETA untuk SHP-101 berpotensi mundur 12 jam akibat gelombang tinggi di perairan Jawa.", "type": "warning", "date": str(today)},
            {"title": "SLA Update", "message": "Pengiriman SHP-098 diselesaikan 4 jam lebih cepat dari target SLA. Terima kasih atas kepercayaan Anda.", "type": "success", "date": str(today - timedelta(days=14))}
        ]
    }


def render_client_portal():
    username = st.session_state.username

    st.markdown(f"""
        <div class="page-header">
            <div class="page-header-icon">🌐</div>
            <div>
                <p class="page-header-title">Portal Klien: {username}</p>
                <p class="page-header-subtitle">Pantau status pengiriman secara real-time</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    data = _demo_client_data(username)

    st.markdown(f"### Selamat Datang, {data['company_name']}")
    st.info("💡 Ini adalah versi beta dari Portal Klien. Data yang ditampilkan saat ini adalah data demo untuk akun Anda.")

    st.markdown("#### 🚢 Pengiriman Aktif")
    active_df = data["active_shipments"]
    if not active_df.empty:
        for _, row in active_df.iterrows():
            st.markdown(f"""
                <div style="background:rgba(14,165,233,0.08); border:1px solid rgba(14,165,233,0.3);
                            border-left:4px solid #0ea5e9; border-radius:12px; padding:16px; margin-bottom:12px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-family:'Outfit',sans-serif; font-weight:700; color:#f0f6ff; font-size:1.05rem;">
                            {row['id']} — {row['vessel']}
                        </span>
                        <span style="background:rgba(251,191,36,0.2); color:#fbbf24; border:1px solid rgba(251,191,36,0.4);
                                     border-radius:99px; padding:2px 10px; font-size:0.75rem; font-weight:700;">
                            {row['status']}
                        </span>
                    </div>
                    <div style="color:#8ba3c0; font-size:0.85rem; display:flex; gap:16px; flex-wrap:wrap;">
                        <span>📍 {row['origin']} → {row['dest']}</span>
                        <span>⏱️ ETA: <strong style="color:#22c55e;">{row['eta']}</strong></span>
                        <span>📦 {row['cargo']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.success("Tidak ada pengiriman aktif saat ini.")

    st.markdown("#### 📜 Riwayat Pengiriman")
    hist_df = data["history"]
    if not hist_df.empty:
        from core.ui.helpers import render_beautiful_table
        render_beautiful_table(hist_df)
        
    st.markdown("<br>#### 🔔 Notifikasi Proaktif", unsafe_allow_html=True)
    if data["notifications"]:
        for notif in data["notifications"]:
            bg_color = "rgba(245,158,11,0.1)" if notif["type"] == "warning" else "rgba(34,197,94,0.1)"
            border_color = "#f59e0b" if notif["type"] == "warning" else "#22c55e"
            icon = "⚠️" if notif["type"] == "warning" else "✅"
            st.markdown(f"""
                <div style="background:{bg_color}; border-left:4px solid {border_color}; padding:12px 16px; border-radius:8px; margin-bottom:10px;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                        <strong style="color:#f0f6ff; font-family:'Outfit',sans-serif;">{icon} {notif['title']}</strong>
                        <span style="color:#8ba3c0; font-size:0.8rem;">{notif['date']}</span>
                    </div>
                    <div style="color:#cbd5e1; font-size:0.9rem;">{notif['message']}</div>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Tidak ada notifikasi baru.")
