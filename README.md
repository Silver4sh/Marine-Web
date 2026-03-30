# MarineOS

Platform analitik dan operasional maritim terintegrasi.

## 🚀 Fitur Utama
- **Monitoring Armada**: Lacak posisi (*live map*), aktivitas, dan anomali kapal laut.
- **Sensor Lingkungan**: Telemetri data laut cerdas via buoy (*salinitas, arus, pasang surut*).
- **Finansial & Klien**: Analisis pendapatan, pengelolaan proyek, serta identifikasi *churn-risk*.
- **Marine AI Analyst**: Prediksi logistik, analisis kognitif bisnis & rekomendasi otomatis.

## 🛠️ Stack Teknologi
- **Frontend**: Streamlit, Plotly, Folium (Peta Interaktif)
- **Backend / DB**: Supabase (PostgreSQL + REST API)
- **Data Analyst**: Pandas & Python `polyfit`

## ⚙️ Cara Menjalankan (Lokal)
1. **Clone Repo & Masuk Folder**:  
   ```bash
   git clone <repo-url> && cd Marine-Web
   ```
2. **Install Dependensi**:  
   ```bash
   pip install -r requirements.txt
   ```
3. **Simpan Credentials Supabase**:  
   Buat file `.streamlit/secrets.toml` dan isi:
   ```toml
   [DB_ACCESS]
   DATABASE_URL = "URL-Proyek-Supabase-Anda"
   database = "API-Key-Anda"
   ```
4. **Jalankan Aplikasi**:  
   ```bash
   streamlit run main.py
   ```

> 🌐 **Live Preview**: Dapat diakses tanpa instalasi kapan saja melalui **[marine.streamlit.app](https://marine.streamlit.app)**

## 📁 Struktur Folder Dasar
- `/assets`: File statis (CSS, template HTML, Javascript, SQL backup).
- `/core`: Logika inti aplikasi, konfigurasi (`config.py`), fungsi utama AI, serta render *View* UI.
- `/db`: Modul koneksi Supabase & File repositori data REST.
- `main.py`: Entry point (Program utama).