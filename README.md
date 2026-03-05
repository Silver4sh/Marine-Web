# Marine-Web (MarineOS)

Platform operasional maritim terintegrasi dengan pemantauan armada real-time, analitik finansial, sistem manajemen survei, dan telemetri sensor lingkungan (buoy).

## 🚀 Fitur Utama

- **Live Fleet Tracking**: Pemantauan kapal secara real-time dengan feed anomali operasi.
- **Enviro Control**: Telemetri sensor buoy (salinitas, arus, pasang surut) dan integrasi peta persebaran (*heatmap*).
- **Marine AI Analyst**: Analitik kognitif cerdas (OpenAI) untuk logistik, keuangan, dan anomali lingkungan.
- **Manajemen Klien & Finansial**: Tracking *order to cash*, pertumbuhan pendapatan, dan risiko *churn* klien.

## 🛠️ Tech Stack & Arsitektur

- **Frontend/UI**: Streamlit (Dashboard interaktif, form, dan peta Folium/Platform).
- **Backend/DB**: **Supabase** (PostgreSQL managed service) dengan Realtime/REST API.
- **Analitik**: Pandas & NumPy (Data processing performa tinggi), Plotly & Altair (Visualisasi tingkat lanjut).

## 📦 Instalasi & Setup Lokal

Aplikasi ini menggunakan Supabase sebagai database cloud. Tidak diperlukan setup database lokal.

1. **Clone repositori**
   ```bash
   git clone <repo-url>
   cd Marine-Web
   ```

2. **Buat Virtual Environment (opsional tapi disarankan)**
   ```bash
   python -m venv env
   source env/bin/activate  # Mac/Linux
   env\Scripts\activate     # Windows
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Secrets**
   Buat folder `.streamlit` dan file `secrets.toml`:
   ```bash
   mkdir .streamlit
   ```
   Isi file `.streamlit/secrets.toml` dengan kredensial Supabase Anda:
   ```toml
   [DB_ACCESS]
   DATABASE_URL = "https://<your-project>.supabase.co"
   database = "<your-anon-or-service-role-key>"
   ```
   *(Opsional)* Anda juga dapat menggunakan file `.env` di root direktori untuk fallback environment variables.

5. **Jalankan Aplikasi**
   ```bash
   streamlit run main.py
   ```
   atau dapat mengakses langsung melalui link berikut: https://marine.streamlit.app/

## 🔐 Keamanan

- Semua input dari User Interface (terutama form login dan registrasi) telah **disanitasi** dan dibatasi secara otomatis (max 64 char).
- Aplikasi menerapkan **Rate Limiting** lokal (maksimal 5x gagal login akan memicu *lockout* selama 5 menit per username).
- Operasi database menggunakan **Supabase Client API** yang lebih aman dari injeksi SQL langsung. 
- *Hashing* password di tingkat aplikasi disiapkan untuk migrasi kredensial (SHA-256).

## 📄 Struktur Proyek Utama

- `main.py` - *Entry point* aplikasi Streamlit.
- `views/` - Halaman-halaman utama (Dashboard, Peta, Lingkungan, Klien, dll).
- `db/repositories/` - Lapisan askes data (*Data Access Layer*) yang membungkus pemanggilan Supabase API.
- `services/` - Lapisan *business logic* (Autentikasi, AI Analyst).
- `components/` - Potongan UI yang dapat digunakan kembali (*Cards, Charts, Helpers*). 